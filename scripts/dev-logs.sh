#!/bin/bash

# Another Doctor - Development Logs Script
# Easy access to logs from different services

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Available services
SERVICES="backend frontend workers postgres redis qdrant minio pgadmin redis-commander prometheus grafana"

show_help() {
    echo "📋 Another Doctor - Development Logs"
    echo "Usage: $0 [service] [options]"
    echo ""
    echo "Available services:"
    echo "  backend              FastAPI backend application"
    echo "  frontend             Next.js frontend application" 
    echo "  workers              Background job workers"
    echo "  postgres             PostgreSQL database"
    echo "  redis                Redis cache/queue"
    echo "  qdrant               Vector database"
    echo "  minio                S3-compatible storage"
    echo "  pgadmin              PostgreSQL admin interface"
    echo "  redis-commander      Redis admin interface"
    echo "  prometheus           Metrics collection"
    echo "  grafana              Metrics visualization"
    echo "  all                  All services"
    echo ""
    echo "Options:"
    echo "  -f, --follow         Follow log output (default)"
    echo "  --tail N             Show last N lines (default: 100)"
    echo "  --since TIME         Show logs since timestamp (e.g., '1h', '30m')"
    echo ""
    echo "Examples:"
    echo "  $0 backend           Show backend logs"
    echo "  $0 backend --tail 50 Show last 50 lines of backend logs"
    echo "  $0 all --since 1h    Show all logs from last hour"
    echo "  $0 postgres -f       Follow PostgreSQL logs"
}

# Parse command line arguments
SERVICE=""
FOLLOW=true
TAIL="100"
SINCE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--follow)
            FOLLOW=true
            shift
            ;;
        --tail)
            TAIL="$2"
            shift 2
            ;;
        --since)
            SINCE="$2"
            shift 2
            ;;
        all)
            SERVICE="all"
            shift
            ;;
        backend|frontend|workers|postgres|redis|qdrant|minio|pgadmin|redis-commander|prometheus|grafana)
            SERVICE="$1"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# If no service specified, show help
if [ -z "$SERVICE" ]; then
    show_help
    exit 1
fi

# Check if docker-compose is running
if ! docker-compose ps > /dev/null 2>&1; then
    print_info "No containers are running. Start the development environment first:"
    echo "  ./scripts/dev-start.sh"
    exit 1
fi

# Build docker-compose logs command
LOGS_CMD="docker-compose logs"

if [ "$FOLLOW" = true ]; then
    LOGS_CMD="$LOGS_CMD -f"
fi

if [ -n "$TAIL" ]; then
    LOGS_CMD="$LOGS_CMD --tail $TAIL"
fi

if [ -n "$SINCE" ]; then
    LOGS_CMD="$LOGS_CMD --since $SINCE"
fi

# Execute logs command
if [ "$SERVICE" = "all" ]; then
    print_info "Showing logs for all services..."
    $LOGS_CMD
else
    # Check if service exists
    if ! echo "$SERVICES" | grep -q "$SERVICE"; then
        echo "Unknown service: $SERVICE"
        show_help
        exit 1
    fi
    
    # Check if service is running
    if ! docker-compose ps "$SERVICE" | grep -q "Up"; then
        print_info "Service '$SERVICE' is not running."
        echo "Available running services:"
        docker-compose ps --services --filter "status=running"
        exit 1
    fi
    
    print_info "Showing logs for $SERVICE..."
    $LOGS_CMD "$SERVICE"
fi