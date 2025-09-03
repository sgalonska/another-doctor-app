# Another Doctor

Medical specialist matching service that parses patient reports and connects them with relevant specialists using evidence-based scoring.

## 🏗️ Monorepo Structure

```
another-doctor/
├── apps/
│   ├── frontend/          # Next.js app (Cloudflare Pages)
│   └── backend/           # FastAPI (patient/admin APIs)
├── packages/
│   ├── shared/            # Cross-language contracts (JSON Schemas, queries)
│   ├── ts-utils/          # Shared TypeScript utilities
│   └── py-utils/          # Shared Python utilities
├── infra/
│   ├── docker/            # Dockerfiles for backend/workers
│   ├── terraform/         # Infrastructure as Code
│   └── cloudflare/        # Cloudflare Workers
├── docs/                  # Documentation
└── .github/workflows/     # CI/CD pipelines
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ and pnpm 8+
- Python 3.11+
- Docker and Docker Compose

### Setup

```bash
# 1. Clone and setup
git clone <repo-url>
cd another-doctor
make setup

# 2. Install all dependencies
make install-all

# 3. Start development services
make dev-up

# 4. Run applications (in separate terminals)
make frontend-dev
make backend-dev
make workers-dev
```

### Development Workflow

```bash
# Frontend development
pnpm run dev:frontend

# Backend development with auto-reload
make backend-dev

# Run tests
make test-all

# Lint all code
make lint-all

# Type checking
pnpm run type-check
```

## 📋 Key Features

- **PHI-Safe Architecture**: No patient data in LLMs, de-identification before processing
- **Evidence-Based Matching**: Transparent scoring using PubMed, ClinicalTrials.gov, NIH data
- **Hybrid Retrieval**: Combines vector search with symbolic filtering
- **Explainable Results**: Full evidence trails for specialist recommendations
- **Modern Stack**: Next.js, FastAPI, Cloudflare Workers, PostgreSQL, Qdrant

## 🛠️ Tech Stack

**Frontend**: Next.js 14, TypeScript, Tailwind CSS, shadcn/ui  
**Backend**: FastAPI, SQLAlchemy, PostgreSQL, Redis, Qdrant  
**Workers**: Cloudflare Workers, RQ/Celery  
**Infrastructure**: Docker, Terraform, Cloudflare  
**External APIs**: PubMed, OpenAlex, ClinicalTrials.gov, NIH RePORTER  

## 📖 Documentation

- [Infrastructure Specification](docs/another-doctor-infra.md)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Shared Schemas](packages/shared/README.md)

## 🔧 Available Commands

See `make help` for all available commands:

```bash
make help                 # Show all available commands
make dev-up              # Start development services
make install-all         # Install all dependencies
make test-all            # Run all tests
make lint-all            # Lint all code
make infra-plan          # Plan infrastructure changes
make deploy-workers      # Deploy to Cloudflare Workers
```

## 🏛️ Architecture

- **Monorepo**: Single source of truth for contracts and atomic changes
- **Microservices**: Separate concerns (frontend, API, workers, edge functions)
- **Event-Driven**: Queue-based processing for case parsing and matching
- **Compliance-First**: PHI protection and audit logging built-in