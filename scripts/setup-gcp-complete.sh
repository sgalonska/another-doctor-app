#!/bin/bash

set -e

echo "🚀 Complete GCP Setup for Another Doctor App"
echo "Domain: app.another.doctor"
echo ""

# Configuration
PROJECT_ID="another-doctor-471116"
REGION="us-central1"
REPO_NAME="another-doctor-prod-repo"
FRONTEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/frontend:latest"
BACKEND_IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/backend:latest"

echo "📋 Project Configuration:"
echo "  Project ID: ${PROJECT_ID}"
echo "  Region: ${REGION}"
echo "  Repository: ${REPO_NAME}"
echo "  Domain: app.another.doctor"
echo ""

# Change to project root
cd "$(dirname "$0")/.."

echo "🔐 Step 1: Authenticating with Google Cloud..."
echo "Checking authentication status..."

# Check if already authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "Not authenticated. Please authenticate:"
    gcloud auth login
fi

# Set project
echo "Setting project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

echo "✅ Authentication complete"
echo ""

echo "🔧 Step 2: Enabling required GCP APIs..."
echo "This may take a few minutes..."

# Enable required APIs
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    compute.googleapis.com \
    iam.googleapis.com \
    cloudresourcemanager.googleapis.com \
    secretmanager.googleapis.com \
    domains.googleapis.com

echo "✅ APIs enabled"
echo ""

echo "📦 Step 3: Setting up Artifact Registry..."

# Check if repository exists, create if not
if ! gcloud artifacts repositories describe ${REPO_NAME} --location=${REGION} >/dev/null 2>&1; then
    echo "Creating Artifact Registry repository..."
    gcloud artifacts repositories create ${REPO_NAME} \
        --repository-format=docker \
        --location=${REGION} \
        --description="Another Doctor production container repository"
else
    echo "Artifact Registry repository already exists"
fi

# Configure Docker authentication
echo "Configuring Docker authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev

echo "✅ Artifact Registry ready"
echo ""

echo "🏗️  Step 4: Building and pushing Docker images..."

# Build frontend
echo "Building frontend Docker image..."
cd apps/frontend
docker build -t ${FRONTEND_IMAGE} .

# Build backend  
echo "Building backend Docker image..."
cd ../backend
docker build -t ${BACKEND_IMAGE} .

cd ../..

echo "Pushing images to Artifact Registry..."
docker push ${FRONTEND_IMAGE}
docker push ${BACKEND_IMAGE}

echo "✅ Docker images ready"
echo ""

echo "🌍 Step 5: Deploying infrastructure with Terraform..."

cd infra/gcp

# Initialize terraform if needed
if [ ! -d ".terraform" ]; then
    terraform init
fi

# Apply infrastructure
echo "Deploying Cloud Run services..."
terraform apply -var-file="environments/prod.tfvars" -auto-approve

cd ../..

echo "✅ Infrastructure deployed"
echo ""

echo "🔗 Step 6: Setting up domain mapping..."

# Get the frontend service URL
FRONTEND_URL=$(gcloud run services describe another-doctor-prod-frontend \
    --platform=managed \
    --region=${REGION} \
    --format="value(status.url)" 2>/dev/null || echo "")

if [ -n "$FRONTEND_URL" ]; then
    echo "Frontend service URL: $FRONTEND_URL"
    
    # Create domain mapping
    echo "Creating domain mapping for app.another.doctor..."
    
    # Check if domain mapping already exists
    if ! gcloud run domain-mappings describe app.another.doctor --region=${REGION} >/dev/null 2>&1; then
        gcloud run domain-mappings create \
            --service=another-doctor-prod-frontend \
            --domain=app.another.doctor \
            --region=${REGION} || echo "Domain mapping creation initiated (may need manual verification)"
    else
        echo "Domain mapping already exists"
    fi
else
    echo "⚠️  Frontend service not found. Skipping domain mapping."
fi

echo ""
echo "🎉 Setup Complete!"
echo ""
echo "📋 Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Get service URLs
FRONTEND_URL=$(terraform -chdir=infra/gcp output -raw frontend_url 2>/dev/null || echo "Getting URL...")
BACKEND_URL=$(terraform -chdir=infra/gcp output -raw backend_url 2>/dev/null || echo "Getting URL...")

echo "🌐 Services Deployed:"
echo "  Frontend: $FRONTEND_URL"
echo "  Backend:  $BACKEND_URL"
echo ""
echo "🔗 Domain Configuration:"
echo "  Custom Domain: app.another.doctor"
echo "  Status: Setting up (may take up to 15 minutes)"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. DNS Configuration (in Cloudflare):"
echo "   → Add CNAME record: app → ghs.googlehosted.com"
echo ""
echo "2. Domain Verification:"
echo "   → Go to Google Cloud Console → Cloud Run → Domains"
echo "   → Verify app.another.doctor domain mapping"
echo "   → This may require domain ownership verification"
echo ""
echo "3. SSL Certificate:"
echo "   → Google will automatically provision SSL certificate"
echo "   → This can take 15-60 minutes after DNS propagation"
echo ""
echo "4. Testing:"
echo "   → Test the temporary Cloud Run URL first"
echo "   → Then test https://app.another.doctor once DNS propagates"
echo ""
echo "🔍 Monitoring:"
echo "   → Cloud Console: https://console.cloud.google.com/run?project=${PROJECT_ID}"
echo "   → Logs: https://console.cloud.google.com/logs/query?project=${PROJECT_ID}"
echo ""
echo "💡 Troubleshooting:"
echo "   → If domain doesn't work after 1 hour, check DNS propagation"
echo "   → Verify domain ownership in Google Search Console if required"
echo "   → Check Cloud Run logs for application errors"
echo ""
echo "✅ Your Another Doctor app is now deployed to Google Cloud!"