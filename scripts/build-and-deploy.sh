#!/bin/bash

set -e

echo "🚀 Building and deploying Another Doctor to GCP..."

# Set up environment
export PROJECT_ID="another-doctor-471116"
export REGION="us-central1"

# Build images using Cloud Build (this uses GCP credentials automatically)
echo "📦 Building backend image using Cloud Build..."
gcloud builds submit --config=cloudbuild-backend.yaml --project=$PROJECT_ID .

echo "📦 Building frontend image using Cloud Build..."
gcloud builds submit --config=cloudbuild-frontend.yaml --project=$PROJECT_ID .

echo "✅ Images built and pushed successfully!"

# Deploy infrastructure
echo "🏗️ Deploying infrastructure..."
cd infra/gcp
terraform apply -var-file="environments/prod.tfvars" -auto-approve
cd ../..

echo "🌐 Setting up domain mapping..."

# Get frontend service URL
FRONTEND_URL=$(gcloud run services describe another-doctor-prod-frontend \
    --platform=managed \
    --region=$REGION \
    --format="value(status.url)" \
    --project=$PROJECT_ID)

echo "Frontend service URL: $FRONTEND_URL"

# Create domain mapping
gcloud run domain-mappings create \
    --service=another-doctor-prod-frontend \
    --domain=app.another.doctor \
    --region=$REGION \
    --project=$PROJECT_ID || echo "Domain mapping already exists"

echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "1. In Cloudflare DNS, add CNAME record:"
echo "   Name: app"
echo "   Target: ghs.googlehosted.com"
echo ""
echo "2. Wait 15-60 minutes for DNS propagation"
echo ""
echo "3. Access your app at: https://app.another.doctor"
echo "   Backend API at: $FRONTEND_URL"