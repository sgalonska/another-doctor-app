.PHONY: help setup dev-up dev-down backend-dev frontend-dev workers-dev clean install-backend install-frontend install-workers migrate

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial project setup
	@echo "Setting up Another Doctor development environment..."
	cp .env.example .env
	@echo "Please edit .env file with your configuration"

dev-up: ## Start complete development environment
	./scripts/dev-start.sh

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

# Combined commands
install-all: install-packages install-backend install-frontend install-workers ## Install all dependencies

dev-all: dev-up ## Start all development services
	@echo "Starting all development services..."
	@echo "Run 'make backend-dev', 'make frontend-dev', and 'make workers-dev' in separate terminals"

lint-all: lint-backend lint-frontend ## Lint all code

test-all: test-backend test-frontend ## Run all tests