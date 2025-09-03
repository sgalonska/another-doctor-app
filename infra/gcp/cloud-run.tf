# Cloud Run services configuration

# Backend API service
resource "google_cloud_run_v2_service" "backend" {
  name     = "${local.name_prefix}-backend"
  location = var.region
  
  template {
    service_account = google_service_account.cloud_run.email
    
    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }

    vpc_access {
      network_interfaces {
        network    = google_compute_network.main.name
        subnetwork = google_compute_subnetwork.main.name
        tags       = ["backend"]
      }
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.main.repository_id}/backend:latest"
      
      ports {
        container_port = 8000
      }

      resources {
        limits = {
          cpu    = "2000m"
          memory = "2Gi"
        }
        cpu_idle = false
        startup_cpu_boost = true
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "DATABASE_URL"
        value = "postgresql://${google_sql_user.main.name}:${random_password.db_password.result}@${google_sql_database_instance.main.private_ip_address}:5432/${google_sql_database.main.name}"
      }

      env {
        name  = "REDIS_URL"
        value = "redis://${google_redis_instance.main.host}:${google_redis_instance.main.port}"
      }

      env {
        name  = "QDRANT_URL"
        value = "http://${google_cloud_run_v2_service.qdrant.uri}"
      }

      env {
        name  = "CLOUD_STORAGE_BUCKET"
        value = google_storage_bucket.main.name
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name = "SECRET_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.app_secret_key.secret_id
            version = "latest"
          }
        }
      }

      env {
        name  = "ALLOWED_HOSTS"
        value = "*.run.app,localhost"
      }

      env {
        name  = "BACKEND_CORS_ORIGINS"
        value = "https://${google_cloud_run_v2_service.frontend.uri},http://localhost:3000"
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 60
        timeout_seconds = 30
        period_seconds = 30
        failure_threshold = 3
      }

      startup_probe {
        http_get {
          path = "/health"
          port = 8000
        }
        initial_delay_seconds = 30
        timeout_seconds = 30
        period_seconds = 10
        failure_threshold = 10
      }
    }
  }

  labels = local.labels

  depends_on = [
    google_project_service.required_apis,
    google_sql_database_instance.main,
    google_redis_instance.main
  ]
}

# Frontend service
resource "google_cloud_run_v2_service" "frontend" {
  name     = "${local.name_prefix}-frontend"
  location = var.region
  
  template {
    service_account = google_service_account.cloud_run.email
    
    scaling {
      min_instance_count = 1
      max_instance_count = 5
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.main.repository_id}/frontend:latest"
      
      ports {
        container_port = 3000
      }

      resources {
        limits = {
          cpu    = "1000m"
          memory = "1Gi"
        }
        cpu_idle = false
      }

      env {
        name  = "NODE_ENV"
        value = "production"
      }

      env {
        name  = "NEXT_PUBLIC_API_URL"
        value = "${google_cloud_run_v2_service.backend.uri}/api/v1"
      }

      env {
        name  = "NEXT_PUBLIC_ENVIRONMENT"
        value = var.environment
      }

      liveness_probe {
        http_get {
          path = "/"
          port = 3000
        }
        initial_delay_seconds = 30
        timeout_seconds = 10
        period_seconds = 30
        failure_threshold = 3
      }
    }
  }

  labels = local.labels

  depends_on = [google_project_service.required_apis]
}

# Workers service
resource "google_cloud_run_v2_service" "workers" {
  name     = "${local.name_prefix}-workers"
  location = var.region
  
  template {
    service_account = google_service_account.cloud_run.email
    
    scaling {
      min_instance_count = 1
      max_instance_count = 5
    }

    vpc_access {
      network_interfaces {
        network    = google_compute_network.main.name
        subnetwork = google_compute_subnetwork.main.name
        tags       = ["workers"]
      }
    }

    containers {
      image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.main.repository_id}/workers:latest"
      
      resources {
        limits = {
          cpu    = "2000m"
          memory = "2Gi"
        }
        cpu_idle = false
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }

      env {
        name  = "DATABASE_URL"
        value = "postgresql://${google_sql_user.main.name}:${random_password.db_password.result}@${google_sql_database_instance.main.private_ip_address}:5432/${google_sql_database.main.name}"
      }

      env {
        name  = "REDIS_URL"
        value = "redis://${google_redis_instance.main.host}:${google_redis_instance.main.port}"
      }

      env {
        name  = "QDRANT_URL"
        value = "http://${google_cloud_run_v2_service.qdrant.uri}"
      }

      env {
        name  = "CLOUD_STORAGE_BUCKET"
        value = google_storage_bucket.main.name
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
    }
  }

  labels = local.labels

  depends_on = [
    google_project_service.required_apis,
    google_sql_database_instance.main,
    google_redis_instance.main
  ]
}

# Qdrant vector database service  
resource "google_cloud_run_v2_service" "qdrant" {
  name     = "${local.name_prefix}-qdrant"
  location = var.region
  
  template {
    scaling {
      min_instance_count = 1
      max_instance_count = 3
    }

    containers {
      image = "qdrant/qdrant:v1.7.0"
      
      ports {
        container_port = 6333
      }

      resources {
        limits = {
          cpu    = "2000m"
          memory = "4Gi"
        }
        cpu_idle = false
      }

      env {
        name  = "QDRANT__SERVICE__HTTP_PORT"
        value = "6333"
      }

      env {
        name  = "QDRANT__LOG_LEVEL"
        value = "INFO"
      }

      volume_mounts {
        name       = "qdrant-storage"
        mount_path = "/qdrant/storage"
      }

      liveness_probe {
        http_get {
          path = "/health"
          port = 6333
        }
        initial_delay_seconds = 60
        timeout_seconds = 10
        period_seconds = 30
        failure_threshold = 3
      }
    }

    volumes {
      name = "qdrant-storage"
      gcs {
        bucket    = google_storage_bucket.qdrant_storage.name
        read_only = false
      }
    }
  }

  labels = local.labels

  depends_on = [google_project_service.required_apis]
}

# Separate bucket for Qdrant storage
resource "google_storage_bucket" "qdrant_storage" {
  name          = "${var.project_id}-${local.name_prefix}-qdrant"
  location      = var.region
  storage_class = "STANDARD"

  uniform_bucket_level_access = true
  public_access_prevention = "enforced"

  labels = local.labels
}

# IAM access for Cloud Run services
resource "google_cloud_run_service_iam_member" "backend_public" {
  location = google_cloud_run_v2_service.backend.location
  project  = google_cloud_run_v2_service.backend.project
  service  = google_cloud_run_v2_service.backend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service_iam_member" "frontend_public" {
  location = google_cloud_run_v2_service.frontend.location
  project  = google_cloud_run_v2_service.frontend.project
  service  = google_cloud_run_v2_service.frontend.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Private access for internal services
resource "google_cloud_run_service_iam_member" "qdrant_internal" {
  location = google_cloud_run_v2_service.qdrant.location
  project  = google_cloud_run_v2_service.qdrant.project
  service  = google_cloud_run_v2_service.qdrant.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.cloud_run.email}"
}