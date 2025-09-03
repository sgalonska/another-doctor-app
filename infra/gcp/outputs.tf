# Output values for the GCP infrastructure

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

# Cloud SQL outputs
output "database_instance_name" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.main.name
}

output "database_private_ip" {
  description = "Cloud SQL private IP address"
  value       = google_sql_database_instance.main.private_ip_address
  sensitive   = true
}

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.main.connection_name
}

# Redis outputs
output "redis_host" {
  description = "Memorystore Redis host"
  value       = google_redis_instance.main.host
  sensitive   = true
}

output "redis_port" {
  description = "Memorystore Redis port"
  value       = google_redis_instance.main.port
}

# Storage outputs
output "storage_bucket_name" {
  description = "Cloud Storage bucket name"
  value       = google_storage_bucket.main.name
}

output "qdrant_storage_bucket_name" {
  description = "Qdrant storage bucket name"
  value       = google_storage_bucket.qdrant_storage.name
}

# Artifact Registry outputs
output "artifact_registry_url" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.main.repository_id}"
}

# Cloud Run service URLs
output "backend_url" {
  description = "Backend Cloud Run service URL"
  value       = google_cloud_run_v2_service.backend.uri
}

output "frontend_url" {
  description = "Frontend Cloud Run service URL"
  value       = google_cloud_run_v2_service.frontend.uri
}

output "workers_url" {
  description = "Workers Cloud Run service URL"
  value       = google_cloud_run_v2_service.workers.uri
}

output "qdrant_url" {
  description = "Qdrant Cloud Run service URL"
  value       = google_cloud_run_v2_service.qdrant.uri
}

# Service Account
output "cloud_run_service_account_email" {
  description = "Cloud Run service account email"
  value       = google_service_account.cloud_run.email
}

# Secret Manager
output "secret_ids" {
  description = "Secret Manager secret IDs"
  value = {
    db_password     = google_secret_manager_secret.db_password.secret_id
    app_secret_key  = google_secret_manager_secret.app_secret_key.secret_id
  }
}

# Network outputs
output "network_name" {
  description = "VPC network name"
  value       = google_compute_network.main.name
}

output "subnet_name" {
  description = "Subnet name"
  value       = google_compute_subnetwork.main.name
}

# Deployment information
output "deployment_info" {
  description = "Key deployment information"
  value = {
    project_id           = var.project_id
    region              = var.region
    environment         = var.environment
    artifact_registry   = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.main.repository_id}"
    backend_url         = google_cloud_run_v2_service.backend.uri
    frontend_url        = google_cloud_run_v2_service.frontend.uri
    storage_bucket      = google_storage_bucket.main.name
  }
}