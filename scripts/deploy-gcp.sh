#!/bin/bash

# Another Doctor - GCP Deployment Script
# Deploys the application to Google Cloud Platform

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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default values
ENVIRONMENT="prod"
PROJECT_ID=""
REGION="us-central1"
SKIP_TERRAFORM=false
SKIP_BUILD=false
SKIP_DEPLOY=false

show_help() {
    echo "🚀 Another Doctor - GCP Deployment Script"
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -p, --project-id ID     GCP Project ID (required)"
    echo "  -r, --region REGION     GCP Region (default: us-central1)"
    echo "  -e, --environment ENV   Environment (dev/staging/prod, default: prod)"
    echo "  --skip-terraform        Skip Terraform infrastructure deployment"
    echo "  --skip-build           Skip Docker image building"
    echo "  --skip-deploy          Skip Cloud Run deployment"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -p my-project-123                    # Full deployment"
    echo "  $0 -p my-project-123 --skip-terraform  # Skip infrastructure setup"
    echo "  $0 -p my-project-123 -e staging        # Deploy to staging"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--project-id)
            PROJECT_ID="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --skip-terraform)
            SKIP_TERRAFORM=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-deploy)
            SKIP_DEPLOY=true
            shift
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

# Validate required parameters
if [ -z "$PROJECT_ID" ]; then
    print_error "Project ID is required. Use -p or --project-id"
    show_help
    exit 1
fi

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    print_error "Environment must be dev, staging, or prod"
    exit 1
fi

print_status "Starting GCP deployment for Another Doctor"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Environment: $ENVIRONMENT"
echo ""

# Check required tools
print_status "Checking required tools..."
command -v gcloud >/dev/null 2>&1 || { print_error "gcloud CLI is required but not installed."; exit 1; }
command -v docker >/dev/null 2>&1 || { print_error "docker is required but not installed."; exit 1; }
if [ "$SKIP_TERRAFORM" = false ]; then
    command -v terraform >/dev/null 2>&1 || { print_error "terraform is required but not installed."; exit 1; }
fi

# Set gcloud project
print_status "Setting gcloud project..."
gcloud config set project "$PROJECT_ID"

# Configure Docker for Artifact Registry
print_status "Configuring Docker authentication..."
gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet

# 1. Deploy Infrastructure with Terraform
if [ "$SKIP_TERRAFORM" = false ]; then
    print_status "Deploying infrastructure with Terraform..."
    
    cd infra/gcp
    
    # Initialize Terraform if needed
    if [ ! -d ".terraform" ]; then
        print_status "Initializing Terraform..."
        terraform init
    fi
    
    # Create terraform.tfvars if it doesn't exist
    if [ ! -f "terraform.tfvars" ]; then
        print_status "Creating terraform.tfvars..."
        cat > terraform.tfvars <<EOF
project_id  = "$PROJECT_ID"
region      = "$REGION"
environment = "$ENVIRONMENT"
app_name    = "another-doctor"
EOF
    fi
    
    # Plan and apply
    print_status "Planning Terraform changes..."
    terraform plan -var-file="terraform.tfvars"
    
    echo ""
    read -p "Do you want to apply these changes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Applying Terraform changes..."
        terraform apply -var-file="terraform.tfvars" -auto-approve
        print_success "Infrastructure deployed successfully!"
    else
        print_warning "Infrastructure deployment skipped."
        if [ "$SKIP_BUILD" = false ] || [ "$SKIP_DEPLOY" = false ]; then
            print_error "Cannot continue without infrastructure. Exiting."
            exit 1
        fi
    fi
    
    # Get outputs
    ARTIFACT_REGISTRY=$(terraform output -raw artifact_registry_url)
    
    cd ../..
else
    print_warning "Skipping Terraform infrastructure deployment"
    # Assume standard naming convention
    ARTIFACT_REGISTRY="$REGION-docker.pkg.dev/$PROJECT_ID/another-doctor-$ENVIRONMENT-repo"
fi

# 2. Build and Push Docker Images
if [ "$SKIP_BUILD" = false ]; then
    print_status "Building and pushing Docker images..."
    
    # Build backend
    print_status "Building backend image..."
    docker build -f infra/docker/backend.Dockerfile -t "$ARTIFACT_REGISTRY/backend:latest" --target production .
    docker push "$ARTIFACT_REGISTRY/backend:latest"
    print_success "Backend image pushed!"
    
    # Build frontend
    print_status "Building frontend image..."
    docker build -f infra/docker/frontend.Dockerfile -t "$ARTIFACT_REGISTRY/frontend:latest" --target production .
    docker push "$ARTIFACT_REGISTRY/frontend:latest"
    print_success "Frontend image pushed!"
    
    # Build workers
    print_status "Building workers image..."
    docker build -f infra/docker/workers.Dockerfile -t "$ARTIFACT_REGISTRY/workers:latest" --target production .
    docker push "$ARTIFACT_REGISTRY/workers:latest"
    print_success "Workers image pushed!"
    
else
    print_warning "Skipping Docker image building"
fi

# 3. Deploy to Cloud Run
if [ "$SKIP_DEPLOY" = false ]; then
    print_status "Deploying services to Cloud Run..."
    
    # The actual Cloud Run deployment is handled by Terraform
    # This section could trigger a terraform apply if needed
    if [ "$SKIP_TERRAFORM" = false ]; then
        print_success "Services deployed via Terraform!"
    else
        print_status "Triggering Cloud Run deployments manually..."
        
        # Manual deployment commands would go here if needed
        # For now, we rely on Terraform to handle the deployments
        print_warning "Manual Cloud Run deployment not implemented. Use Terraform."
    fi
else
    print_warning "Skipping Cloud Run deployment"
fi

# Get service URLs
print_status "Getting service URLs..."
if [ "$SKIP_TERRAFORM" = false ]; then
    cd infra/gcp
    BACKEND_URL=$(terraform output -raw backend_url)
    FRONTEND_URL=$(terraform output -raw frontend_url)
    cd ../..
    
    echo ""
    print_success "Deployment completed successfully!"
    echo ""
    echo "🌐 Service URLs:"
    echo "  Frontend: $FRONTEND_URL"
    echo "  Backend:  $BACKEND_URL"
    echo ""
    echo "🔧 Next steps:"
    echo "  1. Test the deployed services"
    echo "  2. Set up monitoring and alerting"
    echo "  3. Configure custom domain (if needed)"
    echo "  4. Set up CI/CD pipeline"
fi

print_success "GCP deployment script completed!"