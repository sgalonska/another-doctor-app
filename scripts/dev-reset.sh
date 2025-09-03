#!/bin/bash

# Another Doctor - Development Environment Reset Script
# This script completely resets the development environment

set -e

echo "🔄 Another Doctor - Resetting Development Environment"
echo "===================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Confirmation prompt
print_warning "This will completely reset your development environment!"
print_warning "All data in databases, caches, and file storage will be lost!"
echo ""
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Reset cancelled."
    exit 1
fi

print_status "Stopping all containers..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down --remove-orphans

print_status "Removing all volumes..."
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v

print_status "Removing Another Doctor images..."
docker images --format "table {{.Repository}}:{{.Tag}}" | grep -E "(another-doctor|another_doctor)" | awk '{print $1":"$2}' | xargs -r docker rmi -f || true

print_status "Cleaning up Docker system..."
docker system prune -f
docker volume prune -f

print_status "Rebuilding images..."
docker-compose build --no-cache

print_success "Environment reset complete!"
echo ""
echo "🚀 To start the fresh environment:"
echo "   ./scripts/dev-start.sh"
echo ""
echo "🌱 To start with seed data:"
echo "   ./scripts/dev-start.sh --seed"
echo ""
echo "🔧 To start with development tools:"
echo "   ./scripts/dev-start.sh --with-tools"