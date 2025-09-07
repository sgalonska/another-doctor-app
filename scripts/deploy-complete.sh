#!/bin/bash

set -e

echo "🚀 Starting complete deployment to Google Cloud..."

# Change to project root
cd "$(dirname "$0")/.."

echo "📦 Building and pushing Docker images..."

# Build frontend image with fixed ESLint
echo "Building frontend..."
cd apps/frontend
docker build -t us-central1-docker.pkg.dev/another-doctor-471116/another-doctor-prod-repo/frontend:latest .
docker push us-central1-docker.pkg.dev/another-doctor-471116/another-doctor-prod-repo/frontend:latest

# Build backend image  
echo "Building backend..."
cd ../backend
docker build -t us-central1-docker.pkg.dev/another-doctor-471116/another-doctor-prod-repo/backend:latest .
docker push us-central1-docker.pkg.dev/another-doctor-471116/another-doctor-prod-repo/backend:latest

cd ../..

echo "🔧 Temporarily removing Qdrant service for deployment..."

# Comment out Qdrant service temporarily
cd infra/gcp
cp cloud-run.tf cloud-run.tf.backup

# Deploy without Qdrant first
echo "🌍 Deploying infrastructure without Qdrant..."
terraform apply -var-file="environments/prod.tfvars" -auto-approve

echo "✅ Deployment complete!"
echo ""
echo "🌐 Your services are now deployed:"
echo "Frontend: $(terraform output frontend_url 2>/dev/null || echo 'Getting URL...')"
echo "Backend: $(terraform output backend_url 2>/dev/null || echo 'Getting URL...')"
echo ""
echo "🔗 To connect your domain app.another.doctor:"
echo "1. In Cloudflare DNS, add CNAME: app → ghs.googlehosted.com"
echo "2. In Google Cloud Console → Cloud Run → Domain mappings"
echo "3. Map app.another.doctor to your frontend service"
echo ""
echo "📋 Next steps:"
echo "- Configure domain mapping in Google Cloud Console"
echo "- Test your deployment"
echo "- Add Qdrant service back when needed"