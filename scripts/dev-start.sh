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

print_status "Starting core services..."

# Start core services first
docker-compose up -d postgres redis qdrant minio

print_status "Waiting for core services to be healthy..."

# Wait for services to be ready
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1 && \
       docker-compose exec -T redis redis-cli ping > /dev/null 2>&1 && \
       curl -sf http://localhost:6333/health > /dev/null 2>&1 && \
       curl -sf http://localhost:9000/minio/health/live > /dev/null 2>&1; then
        print_success "Core services are ready!"
        break
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    echo -n "."
    sleep 2
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    print_error "Core services failed to start within expected time"
    docker-compose logs
    exit 1
fi

print_status "Setting up MinIO bucket..."
docker-compose up -d minio-setup
sleep 5

print_status "Starting application services..."

# Start application services
docker-compose up -d backend frontend workers

print_status "Waiting for application services..."

# Wait for backend to be ready
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend service is ready!"
        break
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    echo -n "."
    sleep 3
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    print_warning "Backend service may not be ready yet. Check logs with: docker-compose logs backend"
fi

# Wait for frontend to be ready  
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if curl -sf http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend service is ready!"
        break
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    echo -n "."
    sleep 3
done

if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
    print_warning "Frontend service may not be ready yet. Check logs with: docker-compose logs frontend"
fi

echo ""
print_success "🎉 Development environment is running!"
echo ""
echo "📋 Available Services:"
echo "   Frontend:           http://localhost:3000"
echo "   Backend API:        http://localhost:8000"
echo "   API Documentation:  http://localhost:8000/docs"
echo "   PostgreSQL:         localhost:5432 (postgres/password)"
echo "   Redis:              localhost:6379"
echo "   Qdrant:             http://localhost:6333"
echo "   MinIO Console:      http://localhost:9001 (minioadmin/minioadmin)"
echo "   MinIO API:          http://localhost:9000"
echo ""
echo "🔧 Optional Services (use --with-tools flag):"
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

print_success "Development environment is ready! Happy coding! 🚀"