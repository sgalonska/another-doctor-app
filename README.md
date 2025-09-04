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

## 🚀 Local Deployment

### Prerequisites

Before starting, make sure you have installed:

- **Docker** (version 20.0+) - [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose** (version 2.0+) - Usually included with Docker Desktop
- **Git** - For cloning the repository
- **Make** - For using Makefile commands (optional but recommended)
- **Node.js** (version 18+) - Required for package management
- **pnpm** (version 8+) - Package manager (see setup below)

### Package Manager Setup

This project uses **pnpm** as its package manager. If you encounter the error `"packageManager": "yarn@pnpm@8.7.0"`, follow these steps:

#### Option A: Enable Corepack (Recommended)
```bash
# Enable corepack (included with Node.js 16.9+)
corepack enable

# Corepack will automatically install the correct pnpm version
```

#### Option B: Install pnpm manually
```bash
# Install pnpm globally
npm install -g pnpm@8.7.0

# Verify installation
pnpm --version
```

#### Fix Common Issues
```bash
# If you see yarn/pnpm conflicts:
corepack disable yarn
corepack enable pnpm

# Or remove global yarn and use pnpm
npm uninstall -g yarn
npm install -g pnpm@8.7.0
```

### Quick Start (Recommended)

The fastest way to get Another Doctor running locally:

```bash
# 1. Clone the repository
git clone https://github.com/sgalonska/another-doctor-app.git
cd another-doctor-app

# 2. One-command setup (includes Docker containers)
make setup-full

# This will:
# - Check Docker prerequisites
# - Create .env file
# - Build and start all Docker containers
# - Wait for services to be ready (2-3 minutes)
```

**Alternative: Step-by-step setup**
```bash
# 1. Initial setup (prerequisites check + .env file)
make setup

# 2. Start Docker containers
make dev-up
```

**Access your application:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

### Step-by-Step Setup

If you prefer manual setup or want to understand each step:

#### 1. Clone and Configure

```bash
git clone https://github.com/sgalonska/another-doctor-app.git
cd another-doctor-app

# Copy environment template
cp .env.example .env
```

#### 2. Review Environment Configuration

The `.env` file contains all necessary configuration for local development. Default values work out of the box, but you can customize:

```bash
# Optional: Edit configuration
nano .env  # or your preferred editor
```

Key settings for local development:
```env
# Database (auto-configured for Docker)
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=another_doctor

# API endpoints (auto-configured)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
BACKEND_CORS_ORIGINS=http://localhost:3000
```

#### 3. Start Services

**Option A: Complete environment (recommended)**
```bash
make dev-up
```

**Option B: With development tools (database admin, monitoring)**
```bash
make dev-up-tools
```

**Option C: Manual Docker Compose**
```bash
# Start core services first
docker-compose up -d postgres redis qdrant minio

# Wait 30 seconds for services to initialize
sleep 30

# Start application services
docker-compose up -d backend frontend workers
```

#### 4. Verify Installation

Check that all services are running:

```bash
# View running containers
docker-compose ps

# Check service health
curl http://localhost:8000/health    # Backend health
curl http://localhost:3000           # Frontend
curl http://localhost:6333/health    # Qdrant vector DB
```

### Service Overview

Your local development environment includes:

#### Core Application Services
| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Next.js web application |
| Backend | http://localhost:8000 | FastAPI REST API |
| API Docs | http://localhost:8000/docs | Interactive API documentation |
| Workers | (background) | Async job processing |

#### Infrastructure Services
| Service | URL | Credentials |
|---------|-----|-------------|
| PostgreSQL | localhost:5432 | postgres/password |
| Redis | localhost:6379 | (no auth) |
| Qdrant | http://localhost:6333 | (no auth) |
| MinIO | http://localhost:9000 | minioadmin/minioadmin |
| MinIO Console | http://localhost:9001 | minioadmin/minioadmin |

#### Development Tools (with --tools flag)
| Tool | URL | Credentials |
|------|-----|-------------|
| PgAdmin | http://localhost:5050 | admin@anotherdoctor.local/admin |
| Redis Commander | http://localhost:8081 | (no auth) |
| Prometheus | http://localhost:9090 | (no auth) |
| Grafana | http://localhost:3001 | admin/admin |

### Development Workflow

#### Daily Development
```bash
# Start environment
make dev-up

# View logs (all services)
make dev-logs

# View specific service logs
make dev-logs SERVICE=backend
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend

# Stop everything
make dev-down
```

#### Code Changes
```bash
# Backend changes: Auto-reload enabled, no restart needed
# Edit files in apps/backend/

# Frontend changes: Auto-reload enabled, no restart needed  
# Edit files in apps/frontend/

# Database changes: Run migrations
make migrate

# Package changes: Rebuild containers
docker-compose up -d --build backend frontend
```

#### Database Management
```bash
# Database shell
docker-compose exec postgres psql -U postgres -d another_doctor

# Run migrations
make migrate

# Create new migration
make migrate-create name="your_migration_name"

# Reset database (WARNING: deletes all data)
make dev-reset
```

### Troubleshooting

#### Services Won't Start
```bash
# Check Docker is running
docker info

# Check port conflicts (ports may be in use)
lsof -i :3000  # Frontend port
lsof -i :8000  # Backend port
lsof -i :5432  # PostgreSQL port

# Stop conflicting services or change ports in docker-compose.yml
```

#### Permission Issues
```bash
# Fix file permissions (Linux/Mac)
sudo chown -R $USER:$USER .

# Reset Docker volumes
make dev-reset
```

#### Services Not Responding
```bash
# View logs for errors
docker-compose logs backend
docker-compose logs frontend

# Restart specific service
docker-compose restart backend

# Full environment reset
make dev-reset
make dev-up
```

#### Database Connection Issues
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check database connection
docker-compose exec postgres pg_isready -U postgres

# View backend database logs
docker-compose logs backend | grep -i database
```

#### Common Issues & Solutions

**Port 3000 already in use:**
```bash
# Find and kill process using port 3000
lsof -ti:3000 | xargs kill -9
# Or change frontend port in docker-compose.yml
```

**Docker out of space:**
```bash
# Clean up Docker
docker system prune -f
docker volume prune -f
```

**Services start but frontend shows connection errors:**
```bash
# Verify backend is accessible
curl http://localhost:8000/health

# Check CORS configuration in .env
grep CORS .env
```

### Alternative Setup Methods

#### Manual Installation (Without Docker)

If you prefer to run services manually:

```bash
# Install dependencies
make install-all

# Start services in separate terminals:
# Terminal 1: Start backend
make backend-dev

# Terminal 2: Start frontend  
make frontend-dev

# Terminal 3: Start workers
make workers-dev
```

**Prerequisites for manual installation:**
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 6+
- Qdrant vector database

#### Turbo Monorepo Commands

This project uses Turbo for monorepo management:

```bash
# Install all packages
pnpm install

# Start all development servers
pnpm dev

# Build all applications
pnpm build

# Run all tests
pnpm test

# Lint all code
pnpm lint
```

### Next Steps

Once your local environment is running:

1. **Explore the API:** Visit http://localhost:8000/docs
2. **Test the frontend:** Visit http://localhost:3000
3. **View database:** Access PgAdmin at http://localhost:5050
4. **Monitor services:** Check logs with `make dev-logs`
5. **Make changes:** Edit code and see live reload in action

For detailed development workflows, see the [Development Guide](docs/development.md).

## 🚀 Production Deployment

### GCP Production Deployment

```bash
# Deploy to GCP
./scripts/deploy-gcp.sh -p your-gcp-project-id -e prod

# Or use make targets
make deploy-gcp-prod GCP_PROJECT_ID=your-project-id
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