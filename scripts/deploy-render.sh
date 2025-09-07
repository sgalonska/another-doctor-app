#!/bin/bash

# Another Doctor - Render Deployment Script
# This script helps with the deployment process to Render

set -e

echo "🚀 Another Doctor - Render Deployment"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [[ ! -f "render.yaml" ]]; then
    print_error "render.yaml not found. Please run this script from the project root."
    exit 1
fi

# Check if git is initialized
if [[ ! -d ".git" ]]; then
    print_error "Git repository not found. Please initialize git first."
    exit 1
fi

# Step 1: Prepare deployment
echo
print_info "Step 1: Preparing deployment files..."

# Ensure all files are committed
if [[ -n $(git status --porcelain) ]]; then
    print_warning "You have uncommitted changes. Committing them now..."
    git add .
    git commit -m "Prepare for Render deployment" || true
fi

print_success "Deployment files prepared"

# Step 2: Show deployment configuration
echo
print_info "Step 2: Deployment Configuration Summary"
echo "========================================"
echo
echo "📋 Services to be deployed:"
echo "  • Frontend: Next.js app (app.another.doctor)"
echo "  • Backend:  FastAPI app (api.another.doctor)" 
echo "  • Database: PostgreSQL (managed)"
echo "  • Cache:    Redis (managed)"
echo
echo "💰 Estimated monthly cost: $28 (4 × $7 starter services)"
echo

# Step 3: Push to main branch
echo
print_info "Step 3: Pushing to main branch..."

# Ensure we're on main branch
current_branch=$(git branch --show-current)
if [[ "$current_branch" != "main" ]]; then
    print_warning "Not on main branch. Switching to main..."
    git checkout main || git checkout -b main
fi

# Push to main
git push origin main

print_success "Code pushed to main branch"

# Step 4: Deployment instructions
echo
print_info "Step 4: Complete deployment in Render Dashboard"
echo "==============================================="
echo
echo "🌐 Go to: https://dashboard.render.com"
echo
echo "📝 Deployment steps:"
echo "  1. Click 'New +' → 'Blueprint'"
echo "  2. Connect your GitHub repository"
echo "  3. Select 'another-doctor-app' repository"
echo "  4. Render will read render.yaml and create all services"
echo "  5. Wait for all services to deploy (5-10 minutes)"
echo
echo "⚙️  Manual configuration needed:"
echo "  • Set STRIPE_SECRET_KEY in both frontend and backend services"
echo "  • Configure custom domains (app.another.doctor, api.another.doctor)"
echo "  • Update DNS records in Cloudflare:"
echo "    - CNAME: app → another-doctor-frontend.onrender.com"
echo "    - CNAME: api → another-doctor-backend.onrender.com"
echo

# Step 5: Post-deployment checklist
echo
print_info "Step 5: Post-Deployment Checklist"
echo "================================="
echo
echo "✅ Verify these after deployment:"
echo "  □ All services show 'Live' status"
echo "  □ Database connections working"
echo "  □ Frontend loads at https://app.another.doctor"
echo "  □ Backend API responds at https://api.another.doctor"
echo "  □ SSL certificates active"
echo "  □ Environment variables set correctly"
echo "  □ Database migrations completed"
echo

# Step 6: Useful commands
echo
print_info "Step 6: Useful Commands"
echo "======================"
echo
echo "📊 Monitor deployment:"
echo "  • View logs in Render dashboard"
echo "  • Check service metrics"
echo "  • Monitor build progress"
echo
echo "🔧 Local development:"
echo "  • Frontend: ./scripts/run-frontend-local.sh"
echo "  • Backend:  ./scripts/run-backend-local.sh"
echo
echo "📚 Documentation:"
echo "  • Render guide: ./docs/RENDER_DEPLOYMENT_GUIDE.md"
echo "  • API docs: https://api.another.doctor/docs (after deployment)"
echo

print_success "Deployment preparation complete!"
echo
print_info "Next: Complete the deployment in Render Dashboard"
print_info "URL: https://dashboard.render.com"