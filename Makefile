.PHONY: help setup dev-up dev-down backend-dev frontend-dev workers-dev clean install-backend install-frontend install-workers migrate

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial project setup
	@echo "🚀 Setting up Another Doctor development environment..."
	@echo "Checking prerequisites..."
	@command -v docker >/dev/null 2>&1 || { echo "❌ Docker is not installed. Please install Docker first: https://docs.docker.com/get-docker/"; exit 1; }
	@docker info >/dev/null 2>&1 || { echo "❌ Docker is not running. Please start Docker first."; exit 1; }
	@command -v docker-compose >/dev/null 2>&1 || { echo "❌ docker-compose is not installed. Please install docker-compose."; exit 1; }
	@echo "✅ Docker prerequisites check passed"
	@if [ ! -f .env ]; then \
		echo "📄 Creating .env file from template..."; \
		cp .env.example .env; \
		echo "✅ .env file created"; \
	else \
		echo "⚠️  .env file already exists, skipping..."; \
	fi
	@echo "🎉 Setup complete! Run 'make dev-up' to start the development environment."

setup-full: ## Complete setup including Docker container initialization
	@echo "🚀 Running full Another Doctor setup..."
	@$(MAKE) setup
	@echo "🐳 Initializing Docker containers..."
	@echo "This may take several minutes on first run..."
	./scripts/dev-start.sh
	@echo "🎉 Full setup complete! Your development environment is ready."

dev-up: ## Start infrastructure services (DB, Redis, Qdrant)
	./scripts/dev-start.sh

dev-manual: ## Start development environment (infrastructure + manual app servers)
	@echo "🚀 Starting Another Doctor Development Environment (Manual Mode)"
	@echo "============================================================"
	@$(MAKE) dev-up-infra
	@echo ""
	@echo "📋 Next steps:"
	@echo "1. In terminal 1: ./scripts/run-backend-local.sh"
	@echo "2. In terminal 2: ./scripts/run-frontend-local.sh"
	@echo ""
	
dev-up-infra: ## Start only infrastructure services
	docker-compose -f docker-compose.infrastructure.yml up -d

backend-manual: ## Start backend manually
	./scripts/run-backend-local.sh

frontend-manual: ## Start frontend manually  
	./scripts/run-frontend-local.sh

dev-up-tools: ## Start development environment with admin tools
	./scripts/dev-start.sh --with-tools

dev-up-seed: ## Start development environment with seed data
	./scripts/dev-start.sh --seed

dev-down: ## Stop development services
	./scripts/dev-stop.sh

dev-reset: ## Reset development environment (removes all data)
	./scripts/dev-reset.sh

dev-logs: ## Show development logs (usage: make dev-logs SERVICE=backend)
	./scripts/dev-logs.sh $(SERVICE)

install-backend: ## Install backend dependencies
	cd apps/backend && pip install -r requirements.txt && pip install -e ../../packages/py-utils

install-frontend: ## Install frontend dependencies
	cd apps/frontend && npm install

install-workers: ## Install workers dependencies
	cd infra/cloudflare/workers && npm install

install-packages: ## Install shared packages
	cd packages/ts-utils && npm install
	cd packages/py-utils && pip install -e .

backend-dev: ## Start backend development server
	cd apps/backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev: ## Start frontend development server
	cd apps/frontend && npm run dev

workers-dev: ## Start workers development server
	cd infra/cloudflare/workers && npm run dev

migrate: ## Run database migrations
	cd apps/backend && alembic upgrade head

migrate-create: ## Create new migration
	cd apps/backend && alembic revision --autogenerate -m "$(name)"

clean: ## Clean up development environment
	docker-compose down -v
	docker system prune -f

test-backend: ## Run backend tests
	cd apps/backend && python -m pytest

test-frontend: ## Run frontend tests
	cd apps/frontend && npm test

lint-backend: ## Lint backend code
	cd apps/backend && python -m black . && python -m isort . && python -m flake8 .

lint-frontend: ## Lint frontend code
	cd apps/frontend && npm run lint

type-check-frontend: ## Type check frontend
	cd apps/frontend && npm run type-check

deploy-workers: ## Deploy workers to Cloudflare
	cd infra/cloudflare/workers && npm run deploy

# Infrastructure commands
infra-plan: ## Plan terraform changes
	cd infra/terraform && terraform plan -var-file=environments/dev.tfvars

infra-apply: ## Apply terraform changes
	cd infra/terraform && terraform apply -var-file=environments/dev.tfvars

infra-destroy: ## Destroy terraform resources
	cd infra/terraform && terraform destroy -var-file=environments/dev.tfvars

# GCP deployment commands
deploy-gcp-dev: ## Deploy to GCP development environment
	./scripts/deploy-gcp.sh -p $(GCP_PROJECT_ID) -e dev

deploy-gcp-staging: ## Deploy to GCP staging environment
	./scripts/deploy-gcp.sh -p $(GCP_PROJECT_ID) -e staging

deploy-gcp-prod: ## Deploy to GCP production environment
	./scripts/deploy-gcp.sh -p $(GCP_PROJECT_ID) -e prod

gcp-local-test: ## Start GCP-like environment locally
	docker-compose -f docker-compose.gcp.yml up

terraform-plan: ## Plan Terraform infrastructure changes
	cd infra/gcp && terraform plan -var-file="terraform.tfvars"

terraform-apply: ## Apply Terraform infrastructure changes
	cd infra/gcp && terraform apply -var-file="terraform.tfvars"

terraform-destroy: ## Destroy Terraform infrastructure
	cd infra/gcp && terraform destroy -var-file="terraform.tfvars"

# Combined commands
install-all: install-packages install-backend install-frontend install-workers ## Install all dependencies

dev-all: dev-up ## Start all development services
	@echo "Starting all development services..."
	@echo "Run 'make backend-dev', 'make frontend-dev', and 'make workers-dev' in separate terminals"

lint-all: lint-backend lint-frontend ## Lint all code

test-all: test-backend test-frontend ## Run all tests