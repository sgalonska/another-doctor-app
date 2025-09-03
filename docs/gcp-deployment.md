# GCP Deployment Guide

Complete guide for deploying Another Doctor to Google Cloud Platform using Cloud Run, Cloud SQL, Memorystore, and other managed services.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Internet Users                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────┼────────────────────────────────────────┐
│                   Load Balancer                                 │
├────────────────────────┼────────────────────────────────────────┤
│                   Cloud CDN                                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
    ┌────────────────────┼────────────────────┐
    │                    │                    │
┌───▼───┐          ┌────▼────┐         ┌────▼────┐
│Frontend│          │ Backend │         │ Workers │
│Next.js │          │ FastAPI │         │RQ/Celery│
│Cloud Run│         │Cloud Run│         │Cloud Run│
└───┬───┘          └────┬────┘         └────┬────┘
    │                   │                   │
    └───────┬───────────┼───────────────────┘
            │           │
    ┌───────▼───────────▼───────┐
    │        Services           │
    ├─────────┬─────────┬───────┤
    │Cloud SQL│Memorystore│Qdrant│
    │PostgreSQL│ Redis   │Cloud Run
    └─────────┴─────────┴───────┘
            │
    ┌───────▼───────┐
    │Cloud Storage  │
    │   + Bucket    │
    └───────────────┘
```

## 🚀 Quick Deployment

### Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Required tools**:
   ```bash
   # Install gcloud CLI
   curl https://sdk.cloud.google.com | bash
   
   # Install Terraform
   brew install terraform  # macOS
   # or download from https://terraform.io/downloads
   
   # Install Docker
   # Follow instructions at https://docs.docker.com/get-docker/
   ```

3. **GCP Project Setup**:
   ```bash
   # Create new project (or use existing)
   gcloud projects create your-project-id
   gcloud config set project your-project-id
   
   # Enable billing
   gcloud billing projects link your-project-id --billing-account=YOUR_BILLING_ACCOUNT_ID
   ```

### One-Command Deployment

```bash
# Deploy to production
./scripts/deploy-gcp.sh -p your-project-id -e prod

# Deploy to staging
./scripts/deploy-gcp.sh -p your-project-id -e staging
```

## 📋 Detailed Setup

### 1. GCP Project Configuration

```bash
# Set up gcloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Create service account for Terraform
gcloud iam service-accounts create terraform-sa \
    --display-name="Terraform Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:terraform-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/editor"

# Create and download key
gcloud iam service-accounts keys create terraform-key.json \
    --iam-account=terraform-sa@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### 2. Environment Setup

```bash
# Copy environment files
cp .env.production.example .env.production
cp apps/frontend/.env.production.example apps/frontend/.env.production
cp infra/gcp/terraform.tfvars.example infra/gcp/terraform.tfvars

# Edit with your values
nano infra/gcp/terraform.tfvars
```

**Required terraform.tfvars values**:
```hcl
project_id  = "your-gcp-project-id"
region      = "us-central1"
environment = "prod"
app_name    = "another-doctor"
```

### 3. Infrastructure Deployment

```bash
cd infra/gcp

# Initialize Terraform
terraform init

# Plan deployment
terraform plan -var-file="terraform.tfvars"

# Deploy infrastructure
terraform apply -var-file="terraform.tfvars"
```

### 4. Application Deployment

```bash
# Build and deploy using script
./scripts/deploy-gcp.sh -p your-project-id

# Or manually:
# Configure Docker for Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev

# Build images
docker build -f infra/docker/backend.Dockerfile -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/another-doctor-prod-repo/backend:latest --target production .
docker build -f infra/docker/frontend.Dockerfile -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/another-doctor-prod-repo/frontend:latest --target production .
docker build -f infra/docker/workers.Dockerfile -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/another-doctor-prod-repo/workers:latest --target production .

# Push images
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/another-doctor-prod-repo/backend:latest
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/another-doctor-prod-repo/frontend:latest
docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/another-doctor-prod-repo/workers:latest

# Deploy services (handled by Terraform)
terraform apply -var-file="terraform.tfvars"
```

## 🔧 Service Details

### Cloud SQL (PostgreSQL)

- **Instance**: `another-doctor-prod-postgres`
- **Version**: PostgreSQL 15
- **Tier**: `db-g1-small` (adjustable)
- **High Availability**: Regional (primary + replica)
- **Backups**: Daily automated backups with 7-day retention
- **Network**: Private IP only (VPC peering)

**Connection**:
```bash
# Via Cloud SQL Proxy
gcloud sql connect another-doctor-prod-postgres --user=app_user

# Direct connection (from within VPC)
psql -h PRIVATE_IP -U app_user -d another_doctor
```

### Memorystore (Redis)

- **Instance**: `another-doctor-prod-redis`
- **Version**: Redis 7.0
- **Tier**: Standard with high availability
- **Memory**: 1GB (adjustable)
- **Network**: Private VPC access only

### Cloud Run Services

#### Backend API
- **Service**: `another-doctor-prod-backend`
- **Image**: Built from `infra/docker/backend.Dockerfile`
- **Resources**: 2 CPU, 2Gi memory
- **Scaling**: 1-10 instances
- **Health checks**: `/health` endpoint

#### Frontend
- **Service**: `another-doctor-prod-frontend`
- **Image**: Built from `infra/docker/frontend.Dockerfile`
- **Resources**: 1 CPU, 1Gi memory
- **Scaling**: 1-5 instances

#### Workers
- **Service**: `another-doctor-prod-workers`
- **Image**: Built from `infra/docker/workers.Dockerfile`
- **Resources**: 2 CPU, 2Gi memory
- **Scaling**: 1-5 instances

#### Qdrant (Vector Database)
- **Service**: `another-doctor-prod-qdrant`
- **Image**: `qdrant/qdrant:v1.7.0`
- **Resources**: 2 CPU, 4Gi memory
- **Storage**: Cloud Storage bucket mounted
- **Access**: Internal only (via service account)

### Cloud Storage

- **Bucket**: `PROJECT_ID-another-doctor-prod-storage`
- **Location**: Regional (matches Cloud Run region)
- **Access**: Private (service account only)
- **Lifecycle**: 30-day deletion for temporary files
- **CORS**: Configured for frontend uploads

## 🔒 Security Configuration

### Service Account Permissions

The Cloud Run service account has minimal required permissions:
- `roles/cloudsql.client` - Database access
- `roles/redis.editor` - Redis access  
- `roles/storage.objectAdmin` - Storage bucket access
- `roles/secretmanager.secretAccessor` - Secret access

### Network Security

- **Private networking**: All databases use private IPs
- **VPC**: Dedicated VPC with private subnets
- **NAT Gateway**: For outbound internet access
- **Firewall**: Default rules (restrictive)

### Secrets Management

- **Database passwords**: Stored in Secret Manager
- **API keys**: Stored in Secret Manager
- **App secrets**: Generated and stored securely

## 🚦 CI/CD Pipeline

### GitHub Actions Workflow

The deployment pipeline (`.github/workflows/deploy-gcp.yml`) includes:

1. **Testing**:
   - Backend unit tests
   - Frontend tests and linting
   - Type checking

2. **Building**:
   - Docker image builds
   - Push to Artifact Registry
   - Multi-arch support

3. **Deployment**:
   - Terraform infrastructure updates
   - Cloud Run service deployments
   - Database migrations
   - Health checks

4. **Verification**:
   - Service health validation
   - Load testing (staging/prod)
   - Slack notifications

### Required Secrets

Set these in GitHub repository settings:

```
GCP_PROJECT_ID=your-gcp-project-id
GCP_SA_KEY=<service-account-key-json>
SLACK_WEBHOOK_URL=your-slack-webhook-url
```

## 📊 Monitoring & Observability

### Built-in Monitoring

- **Cloud Run**: Automatic metrics (requests, latency, errors)
- **Cloud SQL**: Database performance metrics
- **Memorystore**: Redis metrics
- **Cloud Storage**: Usage and access metrics

### Custom Monitoring

Add to your environment:
```bash
# Optional monitoring services
SENTRY_DSN=your-sentry-dsn
NEW_RELIC_LICENSE_KEY=your-new-relic-key
DATADOG_API_KEY=your-datadog-key
```

### Logging

- **Cloud Logging**: Automatic log aggregation
- **Structured logging**: JSON format in production
- **Log retention**: 30 days default

## 🧪 Testing & Validation

### Local GCP Simulation

Test your production configuration locally:

```bash
# Start GCP-like environment
docker-compose -f docker-compose.gcp.yml up

# Services available at:
# Frontend: http://localhost:3001
# Backend: http://localhost:8001
# Database: localhost:5433
# Redis: localhost:6380
```

### Load Testing

```bash
# Install k6
curl -s https://github.com/grafana/k6/releases/download/v0.45.0/k6-v0.45.0-linux-amd64.tar.gz | tar xz
sudo mv k6-v0.45.0-linux-amd64/k6 /usr/local/bin/

# Run load test against deployed backend
k6 run --vus 10 --duration 5m -e BASE_URL=https://your-backend-url.run.app scripts/load-test.js
```

## 💰 Cost Optimization

### Expected Monthly Costs (USD)

| Service | Configuration | Est. Cost |
|---------|---------------|-----------|
| Cloud Run (3 services) | 1-2 vCPU, minimal traffic | $20-50 |
| Cloud SQL | db-g1-small, regional HA | $50-80 |
| Memorystore | 1GB Standard | $30-40 |
| Cloud Storage | 10GB + requests | $1-5 |
| Artifact Registry | Container storage | $1-5 |
| **Total** | | **$100-180/month** |

### Cost Reduction Tips

1. **Reduce Cloud Run minimum instances** to 0 for dev/staging
2. **Use smaller database tiers** for non-production
3. **Implement Cloud Storage lifecycle policies**
4. **Set up budget alerts**

## 🚨 Troubleshooting

### Common Issues

#### Cloud Run 503 Errors
```bash
# Check service logs
gcloud logs read --service=another-doctor-prod-backend --limit=50

# Check health endpoint
curl https://your-service-url.run.app/health
```

#### Database Connection Issues
```bash
# Test Cloud SQL connectivity
gcloud sql connect another-doctor-prod-postgres --user=app_user

# Check VPC peering
gcloud compute networks peerings list --network=another-doctor-prod-network
```

#### Redis Connection Issues
```bash
# Check Memorystore status
gcloud redis instances describe another-doctor-prod-redis --region=us-central1

# Test from Cloud Shell
gcloud compute ssh test-vm --zone=us-central1-a
redis-cli -h REDIS_IP ping
```

### Service Health Checks

```bash
# Backend health
curl https://your-backend-url.run.app/health

# Frontend health  
curl https://your-frontend-url.run.app/

# Qdrant health
# (Internal only - check from backend logs)
```

## 🔄 Updates & Maintenance

### Application Updates

```bash
# Automated via GitHub Actions on push to main
git push origin main

# Manual deployment
./scripts/deploy-gcp.sh -p your-project-id --skip-terraform
```

### Infrastructure Updates

```bash
cd infra/gcp
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

### Database Maintenance

- **Automated backups**: Daily at 3 AM UTC
- **Maintenance windows**: Sundays 4 AM UTC
- **Minor version updates**: Automatic
- **Major version updates**: Manual approval required

## 🗑️ Cleanup

To destroy all resources:

```bash
# ⚠️  WARNING: This will delete ALL data
cd infra/gcp
terraform destroy -var-file="terraform.tfvars"

# Delete Artifact Registry images
gcloud artifacts docker images delete us-central1-docker.pkg.dev/YOUR_PROJECT_ID/another-doctor-prod-repo --quiet
```

## 📞 Support

For deployment issues:

1. Check the [troubleshooting section](#-troubleshooting)
2. Review Cloud Run logs: `gcloud logs read --service=SERVICE_NAME`
3. Check Terraform state: `terraform show`
4. Open an issue in the GitHub repository

## 📚 Additional Resources

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud SQL for PostgreSQL](https://cloud.google.com/sql/docs/postgres)
- [Memorystore for Redis](https://cloud.google.com/memorystore/docs/redis)
- [Terraform Google Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)