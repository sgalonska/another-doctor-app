terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

# Variables
variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "another-doctor"
}

variable "domain" {
  description = "Custom domain for the application (optional)"
  type        = string
  default     = ""
}

# Providers
provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

# Local values
locals {
  name_prefix = "${var.app_name}-${var.environment}"
  labels = {
    environment = var.environment
    application = var.app_name
    managed_by  = "terraform"
  }
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "cloudsql.googleapis.com",
    "redis.googleapis.com",
    "run.googleapis.com",
    "storage.googleapis.com",
    "container.googleapis.com",
    "compute.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "secretmanager.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com"
  ])

  project = var.project_id
  service = each.value

  disable_on_destroy = false
}

# VPC Network
resource "google_compute_network" "main" {
  name                    = "${local.name_prefix}-network"
  auto_create_subnetworks = false
  
  depends_on = [google_project_service.required_apis]
}

# Subnet
resource "google_compute_subnetwork" "main" {
  name          = "${local.name_prefix}-subnet"
  network       = google_compute_network.main.id
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region

  secondary_ip_range {
    range_name    = "gke-pods"
    ip_cidr_range = "10.1.0.0/16"
  }

  secondary_ip_range {
    range_name    = "gke-services" 
    ip_cidr_range = "10.2.0.0/16"
  }
}

# Cloud NAT for outbound internet access
resource "google_compute_router" "main" {
  name    = "${local.name_prefix}-router"
  region  = var.region
  network = google_compute_network.main.id
}

resource "google_compute_router_nat" "main" {
  name                               = "${local.name_prefix}-nat"
  router                            = google_compute_router.main.name
  region                            = var.region
  nat_ip_allocate_option           = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Artifact Registry for container images
resource "google_artifact_registry_repository" "main" {
  location      = var.region
  repository_id = "${local.name_prefix}-repo"
  description   = "Docker repository for Another Doctor"
  format        = "DOCKER"
  
  labels = local.labels
  
  depends_on = [google_project_service.required_apis]
}

# Cloud SQL (PostgreSQL)
resource "google_sql_database_instance" "main" {
  name                = "${local.name_prefix}-postgres"
  database_version    = "POSTGRES_15"
  region             = var.region
  deletion_protection = true

  settings {
    tier              = "db-g1-small"
    availability_type = "REGIONAL" # For high availability
    disk_type         = "PD_SSD"
    disk_size         = 20
    disk_autoresize   = true

    backup_configuration {
      enabled                        = true
      start_time                    = "03:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = 7
      }
    }

    ip_configuration {
      ipv4_enabled                                  = false
      private_network                              = google_compute_network.main.id
      enable_private_path_for_google_cloud_services = true
    }

    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }

    database_flags {
      name  = "log_connections"
      value = "on"
    }

    database_flags {
      name  = "log_disconnections" 
      value = "on"
    }

    maintenance_window {
      day          = 7
      hour         = 4
      update_track = "stable"
    }
  }

  depends_on = [
    google_project_service.required_apis,
    google_compute_global_address.private_ip_range
  ]
}

# Private IP range for Cloud SQL
resource "google_compute_global_address" "private_ip_range" {
  name          = "${local.name_prefix}-private-ip"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
}

resource "google_service_networking_connection" "private_vpc_connection" {
  network                 = google_compute_network.main.id
  service                 = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_range.name]
}

# Cloud SQL Database and User
resource "google_sql_database" "main" {
  name     = "another_doctor"
  instance = google_sql_database_instance.main.name
}

resource "google_sql_user" "main" {
  name     = "app_user"
  instance = google_sql_database_instance.main.name
  password = random_password.db_password.result
}

resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Memorystore (Redis)
resource "google_redis_instance" "main" {
  name           = "${local.name_prefix}-redis"
  tier           = "STANDARD_HA"
  memory_size_gb = 1
  region         = var.region

  authorized_network = google_compute_network.main.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  redis_version     = "REDIS_7_0"
  display_name      = "Another Doctor Redis"
  
  labels = local.labels

  depends_on = [google_project_service.required_apis]
}

# Cloud Storage bucket
resource "google_storage_bucket" "main" {
  name          = "${var.project_id}-${local.name_prefix}-storage"
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true
  
  public_access_prevention = "enforced"

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30
    }
    action {
      type = "Delete"
    }
  }

  cors {
    origin          = ["https://*.run.app", "https://localhost:3000"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  labels = local.labels
}

# Service Account for Cloud Run services
resource "google_service_account" "cloud_run" {
  account_id   = "${local.name_prefix}-cloud-run"
  display_name = "Cloud Run Service Account"
  description  = "Service account for Another Doctor Cloud Run services"
}

# IAM bindings for service account
resource "google_project_iam_member" "cloud_run_sql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_project_iam_member" "cloud_run_redis" {
  project = var.project_id
  role    = "roles/redis.editor"
  member  = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_storage_bucket_iam_member" "cloud_run_storage" {
  bucket = google_storage_bucket.main.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.cloud_run.email}"
}

# Secret Manager for sensitive configuration
resource "google_secret_manager_secret" "db_password" {
  secret_id = "${local.name_prefix}-db-password"
  
  replication {
    auto {}
  }
  
  labels = local.labels
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

resource "google_secret_manager_secret" "app_secret_key" {
  secret_id = "${local.name_prefix}-app-secret-key"
  
  replication {
    auto {}
  }
  
  labels = local.labels
}

resource "google_secret_manager_secret_version" "app_secret_key" {
  secret      = google_secret_manager_secret.app_secret_key.id
  secret_data = random_password.app_secret_key.result
}

resource "random_password" "app_secret_key" {
  length  = 32
  special = true
}

# IAM for Secret Manager access
resource "google_secret_manager_secret_iam_member" "cloud_run_db_password" {
  secret_id = google_secret_manager_secret.db_password.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
}

resource "google_secret_manager_secret_iam_member" "cloud_run_app_secret" {
  secret_id = google_secret_manager_secret.app_secret_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run.email}"
}