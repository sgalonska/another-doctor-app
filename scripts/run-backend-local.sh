#!/bin/bash

# Another Doctor - Local Backend Development Script
# This script runs the backend manually without Docker

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

print_status "🚀 Starting Another Doctor Backend (Manual Mode)"
print_status "================================================"

# Check if we're in the right directory
if [ ! -f "apps/backend/requirements.txt" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Navigate to backend directory
cd apps/backend

print_status "Setting up Python virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    # Try to use Python 3.11 first (better compatibility), fall back to python3
    if command -v python3.11 > /dev/null 2>&1; then
        python3.11 -m venv venv
    elif command -v python3.10 > /dev/null 2>&1; then
        python3.10 -m venv venv
    else
        python3 -m venv venv
    fi
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

print_status "Upgrading pip..."
pip install --upgrade pip

print_status "Installing core dependencies first..."
if pip install -r requirements-minimal.txt; then
    print_success "Core dependencies installed successfully!"
    print_status "Installing remaining dependencies..."
    pip install -r requirements.txt || print_warning "Some additional dependencies failed to install, but core functionality should work"
else
    print_error "Failed to install even minimal dependencies. Trying individual installation..."
    # Core dependencies needed for basic functionality
    pip install "fastapi==0.104.1" || print_error "Failed to install FastAPI"
    pip install "uvicorn[standard]==0.24.0" || print_error "Failed to install Uvicorn"
    pip install "pydantic==2.5.0" || print_error "Failed to install Pydantic"
    pip install "pydantic-settings==2.1.0" || print_error "Failed to install Pydantic Settings"
    pip install "sqlalchemy==2.0.23" || print_error "Failed to install SQLAlchemy"
    pip install "psycopg[binary]==3.1.12" || print_warning "Failed to install PostgreSQL driver"
    pip install "alembic==1.12.1" || print_error "Failed to install Alembic"
fi

print_status "Installing py-utils package..."
pip install -e ../../packages/py-utils

# Set environment variables for local development
print_status "Setting environment variables..."
export POSTGRES_SERVER="localhost"
export POSTGRES_USER="postgres"
export POSTGRES_PASSWORD="password"
export POSTGRES_DB="another_doctor"
export SQLALCHEMY_DATABASE_URI="postgresql+psycopg://postgres:password@localhost:5432/another_doctor"
export REDIS_URL="redis://localhost:6379"
export QDRANT_URL="http://localhost:6333"
export BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000"
export SECRET_KEY="dev-secret-key-local-development"
export ENVIRONMENT="development"
export ALLOWED_HOSTS="localhost,127.0.0.1"
export PUBMED_API_KEY=""
export CROSSREF_EMAIL="dev@anotherdoctor.local"
# GCP settings for local development
export GCS_BUCKET_NAME="another-doctor-uploads"
export GCP_PROJECT_ID="another-doctor-dev"
export USE_CLOUD_STORAGE="false"

print_status "Running database migrations..."
if ! alembic upgrade head; then
    print_warning "Database migrations failed. This is common on first run."
    print_warning "The server will still start, but database functionality may be limited."
    print_warning "You can run migrations manually later with: cd apps/backend && alembic upgrade head"
fi

print_success "✅ Backend setup complete!"
print_status "Starting development server..."

echo ""
print_success "🎉 Backend will be available at:"
print_success "   API: http://localhost:8000"
print_success "   Documentation: http://localhost:8000/docs"
print_success "   OpenAPI Schema: http://localhost:8000/openapi.json"
echo ""
print_warning "Press Ctrl+C to stop the server"
echo ""

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000