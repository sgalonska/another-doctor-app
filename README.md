# Another Doctor

AI-powered medical specialist matching and case consultation platform.

## 🎯 Overview

Another Doctor helps healthcare professionals find the right specialists for complex medical cases by:
- **Analyzing patient cases** using NLP and medical ontologies
- **Matching with relevant specialists** through hybrid vector + symbolic search
- **Providing consultation workflows** for case discussion and second opinions
- **Ensuring PHI protection** with proper de-identification and security measures

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Frontend     │    │     Backend     │    │     Workers     │
│   (Next.js)     │───▶│   (FastAPI)     │◄──▶│   (RQ/Celery)   │
│   Port: 3000    │    │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────────────────────────────────────┐
         │                   Services                            │
         ├─────────────────┬─────────────────┬─────────────────┤
         │   PostgreSQL    │      Redis      │     Qdrant      │
         │   (Database)    │   (Cache/Jobs)  │  (Vector DB)    │
         └─────────────────┴─────────────────┴─────────────────┘
```

## 🏗️ Project Structure

```
another-doctor-app/
├── apps/
│   ├── backend/           # FastAPI backend application
│   └── frontend/          # Next.js frontend application
├── packages/
│   ├── py-utils/          # Shared Python utilities
│   └── ts-utils/          # Shared TypeScript utilities
├── infra/
│   ├── docker/            # Docker configurations
│   ├── gcp/              # GCP/Terraform infrastructure
│   └── cloudflare/       # Edge workers (future)
├── scripts/              # Development and deployment scripts
└── docs/                 # Documentation
```

## 🚀 Quick Start

### Local Development (Docker)

```bash
# Clone and setup
git clone https://github.com/sgalonska/another-doctor-app.git
cd another-doctor-app

# Start development environment
make dev-up

# Access services:
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### GCP Production Deployment

```bash
# Deploy to GCP
./scripts/deploy-gcp.sh -p your-gcp-project-id -e prod

# Or use make targets
make deploy-gcp-prod GCP_PROJECT_ID=your-project-id
```

### Development Workflow

```bash
# Docker setup (recommended)
make setup          # Initial setup
make dev-up         # Start all services
make dev-logs       # View logs
make dev-down       # Stop services

# Manual setup
make install-all    # Install dependencies
make backend-dev    # Start backend (terminal 1)
make frontend-dev   # Start frontend (terminal 2)
make workers-dev    # Start workers (terminal 3)
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database
- **Redis** - Caching and job queuing
- **Qdrant** - Vector database for embeddings
- **SQLAlchemy** - ORM and database management
- **Alembic** - Database migrations
- **RQ/Celery** - Background job processing

### Frontend
- **Next.js 14** - React framework with App Router
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Modern component library
- **TypeScript** - Type-safe JavaScript

### Infrastructure
- **Docker** - Containerization
- **Google Cloud Platform** - Cloud hosting
  - Cloud Run (containers)
  - Cloud SQL (PostgreSQL)
  - Memorystore (Redis)
  - Cloud Storage (files)
- **Terraform** - Infrastructure as Code
- **GitHub Actions** - CI/CD pipeline

### AI/ML
- **OpenAI GPT** - Case analysis and matching
- **spaCy + scispaCy** - Medical NLP processing
- **Sentence Transformers** - Text embeddings
- **Medical ontologies** - SNOMED, ICD-10, MeSH

## 🧪 Development

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Python 3.11+** (for local backend development)
- **Node.js 18+** (for local frontend development)
- **PostgreSQL 15+** (if not using Docker)

### Testing

```bash
# Run all tests
make test-all

# Individual tests
make test-backend
make test-frontend

# Linting and type checking
make lint-all
make type-check-frontend
```

## 🚀 Deployment

### Development Environment

```bash
# Local Docker environment
make dev-up

# GCP development
make deploy-gcp-dev GCP_PROJECT_ID=your-dev-project
```

### Staging Environment

```bash
# Deploy to staging
make deploy-gcp-staging GCP_PROJECT_ID=your-staging-project

# Test staging deployment
curl https://your-backend-staging-url.run.app/health
```

### Production Environment

```bash
# Deploy to production
make deploy-gcp-prod GCP_PROJECT_ID=your-prod-project

# Monitor deployment
gcloud logs read --service=another-doctor-prod-backend --limit=50
```

See [GCP Deployment Guide](docs/gcp-deployment.md) for detailed instructions.

## 📊 Key Features

### Medical Case Processing
- **PHI De-identification** - Remove sensitive patient data
- **Medical Entity Extraction** - Identify conditions, medications, procedures
- **Case Classification** - Categorize by specialty, urgency, complexity
- **Structured Data Output** - Convert to standardized medical formats

### Specialist Matching
- **Vector Search** - Semantic similarity of cases to specialist expertise
- **Symbolic Search** - Rule-based matching on exact criteria
- **Hybrid Ranking** - Combined scoring algorithm
- **Real-time Results** - Fast matching with caching optimization

### Data Sources Integration
- **PubMed** - Research publications and citations
- **ClinicalTrials.gov** - Clinical trial data
- **NIH RePORTER** - Grant funding information
- **OpenAlex** - Academic publication metadata

### Quality & Compliance
- **HIPAA Compliance** - PHI protection and audit trails
- **Medical Accuracy** - Validation against medical ontologies
- **Performance Monitoring** - Real-time metrics and alerting
- **Scalable Architecture** - Cloud-native design for growth

## 🔒 Security & Compliance

- **PHI Protection** - Comprehensive de-identification
- **Encrypted Storage** - All data encrypted at rest and in transit
- **Access Controls** - Role-based permissions and audit logging
- **Secure APIs** - OAuth2, rate limiting, input validation
- **HIPAA Compliance** - Business associate agreements and safeguards

## 📈 Monitoring & Observability

- **Application Metrics** - Request rates, latency, errors
- **Infrastructure Metrics** - CPU, memory, disk usage
- **Business Metrics** - Case processing, matching accuracy
- **Alerting** - Automated notifications for issues
- **Logging** - Structured logs with correlation IDs

## 📚 Documentation

- [Development Guide](docs/development.md) - Local development setup
- [Docker Guide](docs/docker-development.md) - Container-based development
- [GCP Deployment](docs/gcp-deployment.md) - Production deployment
- [API Reference](docs/api-reference.md) - Backend API documentation
- [Architecture](docs/architecture.md) - System design and decisions

## 🔧 Available Commands

See `make help` for all available commands:

```bash
make help                 # Show all available commands
make dev-up              # Start development services
make deploy-gcp-prod     # Deploy to GCP production
make terraform-plan      # Plan infrastructure changes
make gcp-local-test      # Test GCP configuration locally
```