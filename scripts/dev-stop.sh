#!/bin/bash

# Another Doctor - Development Environment Stop Script

set -e

echo "🛑 Another Doctor - Stopping Development Environment"
echo "=================================================="

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

# Check if --clean flag is provided
CLEAN_FLAG=false
if [[ "$1" == "--clean" ]]; then
    CLEAN_FLAG=true
fi

print_status "Stopping all containers..."

# Stop all containers
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down

if [ $CLEAN_FLAG = true ]; then
    print_warning "Cleaning up volumes and images..."
    
    # Remove volumes (this will delete all data!)
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v
    
    # Remove images
    print_status "Removing Another Doctor images..."
    docker images --format "table {{.Repository}}:{{.Tag}}" | grep "another-doctor" | xargs -r docker rmi || true
    
    # Remove any dangling images
    docker image prune -f
    
    print_success "Environment cleaned up!"
else
    print_success "Development environment stopped."
    print_status "Data volumes preserved. Use --clean flag to remove all data."
fi

echo ""
echo "📝 Useful Commands:"
echo "   Restart environment:    ./scripts/dev-start.sh"
echo "   Clean restart:          ./scripts/dev-stop.sh --clean && ./scripts/dev-start.sh"
echo "   View remaining:         docker ps -a"
echo "   Remove all containers:  docker-compose down --remove-orphans"