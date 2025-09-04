#!/bin/bash

# Another Doctor - Local Frontend Development Script  
# This script runs the frontend manually without Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

print_status "🚀 Starting Another Doctor Frontend (Manual Mode)"
print_status "================================================"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if pnpm is available
if ! command -v pnpm > /dev/null 2>&1; then
    print_warning "pnpm not found, enabling corepack..."
    corepack enable
fi

print_status "Installing workspace dependencies..."
pnpm install

# Navigate to frontend directory
cd apps/frontend

# Set environment variables for local development
print_status "Setting environment variables..."
export NODE_ENV="development"
export NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"
export NEXT_PUBLIC_ENVIRONMENT="development"
# Remove worker URL as we're using GCP
# export NEXT_PUBLIC_WORKERS_URL="http://localhost:8787"

print_success "✅ Frontend setup complete!"
print_status "Starting development server..."

echo ""
print_success "🎉 Frontend will be available at:"
print_success "   Website: http://localhost:3000"
print_success "   Dev Server: Hot reload enabled"
echo ""
print_warning "Press Ctrl+C to stop the server"
echo ""

# Start the development server
pnpm dev