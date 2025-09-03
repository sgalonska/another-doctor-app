terraform {
  required_version = ">= 1.0"
  
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
    postgresql = {
      source  = "cyrilgdn/postgresql"
      version = "~> 1.0"
    }
  }
}

# Variables
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "cloudflare_account_id" {
  description = "Cloudflare Account ID"
  type        = string
  sensitive   = true
}

variable "cloudflare_api_token" {
  description = "Cloudflare API Token"
  type        = string
  sensitive   = true
}

variable "domain" {
  description = "Domain name for the application"
  type        = string
  default     = "anotherdoctor.com"
}

# Providers
provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

# Data sources
data "cloudflare_zone" "main" {
  name = var.domain
}

# R2 Bucket for file uploads
resource "cloudflare_r2_bucket" "uploads" {
  account_id = var.cloudflare_account_id
  name       = "another-doctor-uploads-${var.environment}"
  location   = "auto"
}

# KV Namespace for caching
resource "cloudflare_workers_kv_namespace" "cache" {
  account_id = var.cloudflare_account_id
  title      = "another-doctor-cache-${var.environment}"
}

# DNS Records
resource "cloudflare_record" "api" {
  zone_id = data.cloudflare_zone.main.id
  name    = var.environment == "prod" ? "api" : "api-${var.environment}"
  value   = "your-backend-server.com"  # Update with actual backend URL
  type    = "CNAME"
  proxied = true
}

resource "cloudflare_record" "app" {
  zone_id = data.cloudflare_zone.main.id
  name    = var.environment == "prod" ? "@" : var.environment
  value   = "your-frontend-pages.pages.dev"  # Update with Cloudflare Pages URL
  type    = "CNAME"
  proxied = true
}

# Page Rules for API routing
resource "cloudflare_page_rule" "api_bypass_cache" {
  zone_id  = data.cloudflare_zone.main.id
  target   = "${var.environment == "prod" ? "api" : "api-${var.environment}"}.${var.domain}/api/*"
  priority = 1
  
  actions {
    cache_level = "bypass"
  }
}

# Outputs
output "r2_bucket_name" {
  description = "R2 bucket name for uploads"
  value       = cloudflare_r2_bucket.uploads.name
}

output "kv_namespace_id" {
  description = "KV namespace ID for caching"
  value       = cloudflare_workers_kv_namespace.cache.id
}

output "api_domain" {
  description = "API domain"
  value       = "${var.environment == "prod" ? "api" : "api-${var.environment}"}.${var.domain}"
}

output "app_domain" {
  description = "Application domain"
  value       = var.environment == "prod" ? var.domain : "${var.environment}.${var.domain}"
}