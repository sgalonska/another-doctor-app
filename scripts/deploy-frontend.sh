#!/bin/bash

# Another Doctor - Frontend Only Deployment Script
# Quickly deploy frontend changes to Google Cloud Storage

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default values
PROJECT_ID="another-doctor-471116"
ENVIRONMENT="prod"

show_help() {
    echo "🚀 Another Doctor - Frontend Deployment Script"
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -p, --project-id ID     GCP Project ID (default: another-doctor-471116)"
    echo "  -e, --environment ENV   Environment (dev/staging/prod, default: prod)"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -p my-project-123"
    echo "  $0 -p my-project-123 -e staging"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--project-id)
            PROJECT_ID="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# PROJECT_ID is now set by default, but can be overridden

print_status "Deploying frontend for Another Doctor"
echo "  Project ID: $PROJECT_ID"
echo "  Environment: $ENVIRONMENT"
echo ""

# Check required tools
command -v pnpm >/dev/null 2>&1 || { print_error "pnpm is required but not installed."; exit 1; }
command -v gsutil >/dev/null 2>&1 || { print_error "gsutil is required but not installed."; exit 1; }

# Set gcloud project
print_status "Setting gcloud project..."
gcloud config set project "$PROJECT_ID"

# Build frontend static files
print_status "Building frontend static files..."
cd apps/frontend

# Get backend URL from Terraform if available
if [ -d "../../infra/gcp/.terraform" ]; then
    BACKEND_URL=$(terraform -chdir=../../infra/gcp output -raw backend_url 2>/dev/null || echo "")
    if [ -n "$BACKEND_URL" ]; then
        print_status "Using backend URL from Terraform: $BACKEND_URL"
        NEXT_PUBLIC_API_URL="${BACKEND_URL}/api/v1"
    else
        print_status "Using default backend URL pattern"
        NEXT_PUBLIC_API_URL="https://another-doctor-${ENVIRONMENT}-backend-[hash].run.app/api/v1"
    fi
else
    print_status "Terraform not initialized, using default backend URL pattern"
    NEXT_PUBLIC_API_URL="https://another-doctor-${ENVIRONMENT}-backend-[hash].run.app/api/v1"
fi

# Install dependencies and build
pnpm install
NEXT_PUBLIC_API_URL="$NEXT_PUBLIC_API_URL" pnpm build:static
print_success "Frontend static files built!"

# Deploy to Cloud Storage
print_status "Deploying frontend to Cloud Storage..."
FRONTEND_BUCKET="${PROJECT_ID}-another-doctor-${ENVIRONMENT}-frontend"

# Sync files to bucket
gsutil -m rsync -r -d ./out gs://$FRONTEND_BUCKET/

# Set cache control headers
gsutil -m setmeta -h "Cache-Control:public, max-age=31536000" gs://$FRONTEND_BUCKET/_next/static/**
gsutil -m setmeta -h "Cache-Control:public, max-age=3600" gs://$FRONTEND_BUCKET/*.html
gsutil -m setmeta -h "Cache-Control:public, max-age=86400" gs://$FRONTEND_BUCKET/*.js
gsutil -m setmeta -h "Cache-Control:public, max-age=86400" gs://$FRONTEND_BUCKET/*.css

print_success "Frontend deployed to Cloud Storage!"

cd ../..

echo ""
print_success "Frontend deployment completed successfully!"
echo ""
echo "🌐 Frontend URLs:"
echo "  Storage: https://storage.googleapis.com/${FRONTEND_BUCKET}/index.html"
echo "  CDN: Check your Cloud CDN configuration"
echo ""
echo "💡 Tips:"
echo "  - CDN may take a few minutes to update"
echo "  - Use CloudFlare or similar for custom domain"
echo "  - Check Cloud Console for any issues"