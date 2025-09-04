#!/bin/bash

# Another Doctor - Development Environment Startup Script
# This script starts the complete local development environment

set -e

echo "🚀 Another Doctor - Starting Development Environment"
echo "=================================================="

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

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    print_error "docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

print_status "Checking for existing containers..."

# Stop any existing containers
if [ "$(docker-compose ps -q)" ]; then
    print_warning "Found existing containers. Stopping them..."
    docker-compose down
fi

print_status "Starting infrastructure services..."

# Start infrastructure services (no MinIO for GCP deployment)
docker-compose -f docker-compose.infrastructure.yml up -d

print_status "Waiting for core services to be healthy..."

# Wait for services to be ready
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if docker-compose -f docker-compose.infrastructure.yml exec -T postgres pg_isready -U postgres > /dev/null 2>&1 && \
       docker-compose -f docker-compose.infrastructure.yml exec -T redis redis-cli ping > /dev/null 2>&1 && \
       curl -sf http://localhost:6333/readyz > /dev/null 2>&1; then
        print_success "Infrastructure services are ready!"
        break
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    echo -n "."
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    print_error "Infrastructure services failed to start within expected time"
    print_error "Diagnosing issues..."
    
    # Check individual services
    echo "Checking PostgreSQL..."
    if ! docker-compose -f docker-compose.infrastructure.yml exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
        print_error "PostgreSQL is not ready"
        docker-compose -f docker-compose.infrastructure.yml logs --tail=10 postgres
    fi
    
    echo "Checking Redis..."
    if ! docker-compose -f docker-compose.infrastructure.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
        print_error "Redis is not ready"
        docker-compose -f docker-compose.infrastructure.yml logs --tail=10 redis
    fi
    
    echo "Checking Qdrant..."
    if ! curl -sf http://localhost:6333/readyz > /dev/null 2>&1; then
        print_error "Qdrant is not ready (testing /readyz endpoint)"
        docker-compose -f docker-compose.infrastructure.yml logs --tail=10 qdrant
    fi
    
    print_error "Try running 'docker-compose ps' to check container status"
    print_error "Or run 'make dev-logs' to see detailed logs"
    exit 1
fi

print_success "🎉 Infrastructure services are running!"

echo ""
print_success "📋 Available Infrastructure Services:"
print_success "   PostgreSQL:         localhost:5432 (postgres/password)"
print_success "   Redis:              localhost:6379"  
print_success "   Qdrant:             http://localhost:6333"

echo ""
print_success "📝 Next Steps:"
print_success "   1. Start Backend:   ./scripts/run-backend-local.sh"
print_success "   2. Start Frontend:  ./scripts/run-frontend-local.sh"
echo ""
print_success "🔧 Optional Services (use --with-tools flag):"
echo "   PgAdmin:            http://localhost:5050 (admin@anotherdoctor.local/admin)"
echo "   Redis Commander:    http://localhost:8081"
echo "   Prometheus:         http://localhost:9090"
echo "   Grafana:            http://localhost:3001 (admin/admin)"
echo ""
echo "📝 Useful Commands:"
echo "   View logs:          docker-compose logs -f [service]"
echo "   Restart service:    docker-compose restart [service]"
echo "   Stop all:           docker-compose down"
echo "   Database shell:     docker-compose exec postgres psql -U postgres -d another_doctor"
echo "   Redis shell:        docker-compose exec redis redis-cli"
echo "   Backend shell:      docker-compose exec backend bash"
echo ""

# Check if --with-tools flag is provided
if [[ "$1" == "--with-tools" ]]; then
    print_status "Starting development tools..."
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d pgadmin redis-commander prometheus grafana
    echo "🔧 Development tools started!"
    echo "   PgAdmin:            http://localhost:5050"
    echo "   Redis Commander:    http://localhost:8081" 
    echo "   Prometheus:         http://localhost:9090"
    echo "   Grafana:            http://localhost:3001"
fi

# Check if --seed flag is provided
if [[ "$1" == "--seed" ]] || [[ "$2" == "--seed" ]]; then
    print_status "Seeding development database..."
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm db-seed
    print_success "Database seeded with development data!"
fi

print_success "Infrastructure is ready! Start your app servers manually. 🚀"