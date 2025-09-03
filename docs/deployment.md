# Deployment Guide

Complete guide for deploying Another Doctor to production environments.

## 🏗️ Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│  Cloudflare     │───▶│   Cloudflare    │───▶│    Backend      │
│   Pages         │    │    Workers      │    │  (Render/Fly)   │
│  (Frontend)     │    │  (Edge APIs)    │    │                 │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │                 │    │                 │
                       │   Cloudflare    │    │   Supabase      │
                       │       R2        │    │  (Postgres)     │
                       │   (Storage)     │    │    Redis        │
                       │                 │    │    Qdrant       │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Production Deployment

### Prerequisites

- Cloudflare account with domain
- GitHub repository
- Docker registry account
- Cloud hosting account (Render, Fly.io, etc.)

### 1. Infrastructure Setup

```bash
# Clone and setup
git clone https://github.com/your-org/another-doctor.git
cd another-doctor

# Configure Terraform
cd infra/terraform
cp environments/prod.tfvars.example environments/prod.tfvars
# Edit with your Cloudflare credentials

# Deploy infrastructure
terraform init
terraform plan -var-file=environments/prod.tfvars
terraform apply -var-file=environments/prod.tfvars
```

### 2. Environment Configuration

Set these secrets in your deployment platform:

```bash
# Database
DATABASE_URL="postgresql://user:pass@host:5432/another_doctor"
REDIS_URL="redis://host:6379"
QDRANT_URL="https://your-cluster.qdrant.io"
QDRANT_API_KEY="your-qdrant-key"

# Storage
R2_ENDPOINT_URL="https://your-account-id.r2.cloudflarestorage.com"
R2_ACCESS_KEY_ID="your-r2-access-key"  
R2_SECRET_ACCESS_KEY="your-r2-secret"
R2_BUCKET_NAME="another-doctor-uploads-prod"

# Payment
STRIPE_PUBLIC_KEY="pk_live_..."
STRIPE_SECRET_KEY="sk_live_..."
STRIPE_WEBHOOK_SECRET="whsec_..."

# External APIs
PUBMED_API_KEY="your-pubmed-key"
CROSSREF_EMAIL="your-email@domain.com"

# Security
SECRET_KEY="your-super-secret-production-key"
ALLOWED_HOSTS="anotherdoctor.com,api.anotherdoctor.com"
BACKEND_CORS_ORIGINS="https://anotherdoctor.com"
```

### 3. Deploy Components

**Frontend (Cloudflare Pages):**
```bash
# Build and deploy
pnpm build:frontend
# Cloudflare Pages will auto-deploy from GitHub
```

**Backend (Container Platform):**
```bash
# Build Docker image
docker build -f infra/docker/backend.Dockerfile -t another-doctor-backend .

# Deploy to your platform (example: Render)
# Platform will pull image and deploy automatically
```

**Workers (Cloudflare):**
```bash
# Deploy edge functions
cd infra/cloudflare/workers
npm run deploy
```

## 🔧 Detailed Deployment Steps

### Database Setup

**Option 1: Supabase (Recommended)**

1. Create Supabase project
2. Get connection string from dashboard
3. Run migrations:
   ```bash
   export DATABASE_URL="postgresql://..."
   cd apps/backend
   alembic upgrade head
   ```

**Option 2: Self-hosted PostgreSQL**

```bash
# Using Docker
docker run -d \
  --name postgres-prod \
  -e POSTGRES_DB=another_doctor \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  postgres:15

# Run migrations
cd apps/backend
DATABASE_URL="postgresql://admin:secure_password@localhost:5432/another_doctor" \
alembic upgrade head
```

### Vector Database (Qdrant)

**Option 1: Qdrant Cloud (Recommended)**

1. Sign up at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create cluster and get API key
3. Configure `QDRANT_URL` and `QDRANT_API_KEY`

**Option 2: Self-hosted**

```bash
# Docker deployment
docker run -d \
  --name qdrant-prod \
  -p 6333:6333 \
  -p 6334:6334 \
  -v qdrant_data:/qdrant/storage \
  qdrant/qdrant:latest
```

### File Storage (Cloudflare R2)

1. Create R2 bucket in Cloudflare dashboard
2. Generate API tokens with R2 permissions
3. Configure CORS policy:
   ```json
   {
     "AllowedOrigins": ["https://anotherdoctor.com"],
     "AllowedMethods": ["GET", "PUT", "POST"],
     "AllowedHeaders": ["*"],
     "MaxAgeSeconds": 3600
   }
   ```

### Container Deployment

**Render.com:**
```yaml
# render.yaml
services:
  - type: web
    name: another-doctor-backend
    env: docker
    dockerfilePath: ./infra/docker/backend.Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: postgres
          property: connectionString
    scaling:
      minInstances: 1
      maxInstances: 10

databases:
  - name: postgres
    databaseName: another_doctor
    user: admin
```

**Fly.io:**
```toml
# fly.toml
app = "another-doctor-backend"
primary_region = "ord"

[http_service]
  internal_port = 8000
  force_https = true

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"

[env]
  PORT = "8000"
```

### Cloudflare Workers Deployment

```bash
cd infra/cloudflare/workers

# Set secrets
npx wrangler secret put R2_ACCESS_KEY_ID
npx wrangler secret put R2_SECRET_ACCESS_KEY  
npx wrangler secret put BACKEND_API_URL
npx wrangler secret put STRIPE_WEBHOOK_SECRET

# Deploy
npm run deploy
```

### Frontend Deployment

**Cloudflare Pages:**

1. Connect GitHub repository
2. Set build settings:
   - Build command: `pnpm build:frontend`
   - Build output: `apps/frontend/.next`
   - Root directory: `/`

3. Environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://api.anotherdoctor.com/api/v1
   NEXT_PUBLIC_WORKERS_URL=https://api.anotherdoctor.com
   NEXT_PUBLIC_STRIPE_PUBLIC_KEY=pk_live_...
   ```

**Vercel Alternative:**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd apps/frontend
vercel --prod
```

## 🔐 Security Configuration

### SSL/TLS Setup

Cloudflare automatically provides SSL. For self-hosted:

```bash
# Generate certificates with Let's Encrypt
sudo certbot --nginx -d api.anotherdoctor.com
```

### Firewall Rules

```bash
# Basic UFW setup
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### Security Headers

Configure in Cloudflare or reverse proxy:

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
```

## 📊 Monitoring Setup

### Health Checks

```bash
# Backend health endpoint
curl https://api.anotherdoctor.com/health

# Database connection check
curl https://api.anotherdoctor.com/health/db

# External API check  
curl https://api.anotherdoctor.com/health/external
```

### Log Aggregation

**Cloudflare Analytics:**
- Real User Monitoring enabled
- Core Web Vitals tracking
- Error rate monitoring

**Application Logs:**
```python
# Structured logging in production
import structlog
logger = structlog.get_logger()

logger.info("case_processed", 
           case_id=case_id,
           processing_time=elapsed,
           match_count=len(matches))
```

### Performance Monitoring

```yaml
# Docker Compose monitoring stack
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
      
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

## 🧪 Staging Environment

### Staging Setup

```bash
# Deploy to staging
terraform apply -var-file=environments/staging.tfvars

# Deploy applications with staging config
ENVIRONMENT=staging make deploy-all
```

### Testing Pipeline

```bash
# Run integration tests against staging
ENVIRONMENT=staging make test-integration

# Load testing
k6 run --env ENVIRONMENT=staging tests/load/api-load-test.js
```

## 🚨 Disaster Recovery

### Database Backup

```bash
# Automated daily backups
#!/bin/bash
# backup-db.sh
DATE=$(date +%Y-%m-%d)
pg_dump $DATABASE_URL | gzip > "backup-$DATE.sql.gz"
aws s3 cp "backup-$DATE.sql.gz" s3://backups/database/
```

### Recovery Procedures

```bash
# Restore from backup
gunzip -c backup-2024-09-03.sql.gz | psql $DATABASE_URL

# Verify data integrity
cd apps/backend
python -c "
from app.models import Doctor, CaseSpec
print(f'Doctors: {Doctor.count()}')
print(f'Cases: {CaseSpec.count()}')
"
```

## 🔄 CI/CD Pipeline

GitHub Actions automatically handles deployment:

1. **On PR**: Run tests, linting, type checking
2. **On main branch**: Deploy to staging
3. **On release tag**: Deploy to production

### Manual Deployment Commands

```bash
# Deploy specific component
make deploy-frontend
make deploy-backend  
make deploy-workers
make deploy-infrastructure

# Full deployment
make deploy-all
```

## 📈 Scaling Considerations

### Auto-scaling Configuration

**Horizontal Scaling:**
- Frontend: Cloudflare Pages (automatic)
- Backend: Configure auto-scaling in hosting platform
- Workers: Cloudflare handles automatically

**Database Scaling:**
- Read replicas for heavy queries
- Connection pooling (PgBouncer)
- Query optimization with indexes

**Monitoring Thresholds:**
- CPU > 70%: Scale up
- Memory > 80%: Scale up  
- Response time > 2s: Scale up

## 🐛 Troubleshooting

### Common Issues

**Database Connection Errors:**
```bash
# Check connection
pg_isready -d $DATABASE_URL

# Check connection pool
docker logs backend-container | grep "connection"
```

**File Upload Issues:**
```bash
# Check R2 credentials
aws s3 ls --endpoint-url=$R2_ENDPOINT_URL

# Test presigned URLs
curl -X PUT "presigned-url" --upload-file test.txt
```

**Vector Search Issues:**
```bash
# Check Qdrant health
curl https://your-cluster.qdrant.io/health

# Check collections
curl https://your-cluster.qdrant.io/collections
```

### Emergency Rollback

```bash
# Rollback to previous version
git revert HEAD
git push origin main

# Or rollback specific component
cd infra/cloudflare/workers
npm run deploy -- --compatibility-date 2024-09-01
```

## 📚 Additional Resources

- [Infrastructure Specification](another-doctor-infra.md)
- [Monitoring Guide](monitoring.md)
- [Security Best Practices](security.md)
- [Performance Tuning](performance.md)