#!/bin/bash

# Render CLI Setup Script
# This script helps set up the Render CLI for advanced operations

set -e

echo "🔧 Render CLI Setup"
echo "=================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

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

# Check if Render CLI is installed
if ! command -v render &> /dev/null; then
    print_info "Installing Render CLI..."
    
    # Install Render CLI
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install render
        else
            print_error "Homebrew not found. Please install Homebrew first or use manual installation."
            echo "Manual installation: https://render.com/docs/cli"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://cli.render.com/install | sh
    else
        print_error "Unsupported OS. Please install manually: https://render.com/docs/cli"
        exit 1
    fi
    
    print_success "Render CLI installed"
else
    print_success "Render CLI already installed"
fi

# Set up API key securely
print_info "Setting up Render API key..."

# Check if API key is already configured
if render auth status &> /dev/null; then
    print_warning "API key already configured. Use 'render auth logout' to change."
else
    print_info "Please run: render auth login"
    print_info "Or set environment variable: export RENDER_API_KEY=your_api_key"
fi

# Show useful CLI commands
echo
print_info "Useful Render CLI Commands:"
echo "=========================="
echo
echo "📋 Service Management:"
echo "  render services list                    # List all services"
echo "  render services get <service-id>        # Get service details"
echo "  render services deploy <service-id>     # Trigger deployment"
echo
echo "📊 Monitoring:"
echo "  render services logs <service-id>       # View service logs"
echo "  render services events <service-id>     # View service events"
echo
echo "🗄️  Database Management:"
echo "  render databases list                   # List databases"
echo "  render databases get <db-id>            # Get database details"
echo
echo "🌐 Domain Management:"
echo "  render domains list                     # List custom domains"
echo "  render domains create <domain>          # Add custom domain"
echo
echo "📁 Project Management:"
echo "  render blueprints create                # Create from render.yaml"
echo "  render blueprints sync                  # Sync blueprint changes"
echo

print_success "Render CLI setup complete!"
echo
print_info "Next steps:"
print_info "1. Authenticate: render auth login"
print_info "2. List services: render services list"
print_info "3. Deploy: Use web interface or render blueprints create"