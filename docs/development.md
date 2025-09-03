# Development Guide

This guide covers setting up your development environment and working with the Another Doctor codebase.

## 🚀 Quick Start

### Prerequisites

- **Node.js**: 18.0+ with pnpm 8.0+
- **Python**: 3.11+ with pip
- **Docker**: Latest version with Docker Compose
- **Git**: Latest version

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/your-org/another-doctor.git
cd another-doctor

# Copy environment configuration
make setup

# Install all dependencies (this takes a few minutes)
make install-all

# Start development services
make dev-up
```

### Running the Application

Open 3 terminal windows and run:

```bash
# Terminal 1: Frontend (Next.js)
make frontend-dev
# → http://localhost:3000

# Terminal 2: Backend (FastAPI)
make backend-dev  
# → http://localhost:8000

# Terminal 3: Workers (Cloudflare Workers local)
make workers-dev
# → http://localhost:8787
```

### Verify Setup

```bash
# Check all services are running
curl http://localhost:3000      # Frontend
curl http://localhost:8000/health  # Backend
curl http://localhost:8787/health  # Workers

# Run tests
make test-all

# Check code quality
make lint-all
```

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│    Frontend     │───▶│   Cloudflare    │───▶│     Backend     │
│   (Next.js)     │    │    Workers      │    │   (FastAPI)     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │                 │    │                 │
                       │   Cloudflare    │    │   PostgreSQL    │
                       │       R2        │    │     Redis       │
                       │   (File Store)  │    │     Qdrant      │
                       │                 │    │                 │
                       └─────────────────┘    └─────────────────┘
```

## 🛠️ Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Frontend: Edit files in `apps/frontend/`
   - Backend: Edit files in `apps/backend/`
   - Shared: Edit schemas in `packages/shared/`

3. **Test your changes**
   ```bash
   make test-all      # Run all tests
   make lint-all      # Check code quality
   pnpm type-check    # TypeScript type checking
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

### Code Organization

```
apps/
├── frontend/           # Next.js application
│   ├── src/app/       # App router pages
│   ├── src/components/# Reusable components
│   └── src/lib/       # Frontend utilities
└── backend/           # FastAPI application
    ├── app/api/       # API route handlers
    ├── app/services/  # Business logic
    ├── app/models/    # Database models
    └── app/schemas/   # Pydantic schemas

packages/
├── shared/            # Cross-language contracts
├── ts-utils/          # TypeScript utilities
└── py-utils/          # Python utilities
```

### Working with Schemas

The monorepo uses shared schemas to ensure contract consistency:

```typescript
// Frontend validation
import { CaseJSONSchema } from '@another-doctor/ts-utils';

const validateCase = (data: unknown) => {
  return CaseJSONSchema.parse(data);
};
```

```python
# Backend validation
from another_doctor_utils import validate_case_json

def process_case(case_data: dict):
    validate_case_json(case_data)  # Throws if invalid
    # Process case...
```

## 🧪 Testing

### Running Tests

```bash
# All tests
make test-all

# Frontend only
cd apps/frontend && npm test

# Backend only  
cd apps/backend && python -m pytest

# Specific test file
cd apps/backend && python -m pytest tests/test_matching.py
```

### Writing Tests

**Frontend Tests** (Jest + React Testing Library):
```typescript
// apps/frontend/src/components/__tests__/Button.test.tsx
import { render, screen } from '@testing-library/react';
import { Button } from '../Button';

test('renders button with text', () => {
  render(<Button>Click me</Button>);
  expect(screen.getByRole('button')).toHaveTextContent('Click me');
});
```

**Backend Tests** (pytest):
```python
# apps/backend/tests/test_case_parser.py
import pytest
from app.services.case_parser import CaseParserService

def test_parse_critical_limb_ischemia():
    parser = CaseParserService()
    text = "Patient has critical limb ischemia in left foot"
    
    result = parser.parse_medical_text(text)
    
    assert result['condition']['text'] == 'critical limb ischemia'
    assert result['anatomy']['laterality'] == 'left'
    assert result['anatomy']['site'] == 'foot'
```

## 🔧 Database Operations

### Running Migrations

```bash
# Create new migration
make migrate-create name="add_new_table"

# Apply migrations
make migrate

# Reset database (dev only)
docker-compose down -v
docker-compose up -d postgres
make migrate
```

### Database Access

```bash
# Connect to development database
docker-compose exec postgres psql -U postgres -d another_doctor

# View tables
\dt

# Query data
SELECT * FROM doctor LIMIT 5;
```

## 🐛 Debugging

### Backend Debugging

```bash
# View logs
docker-compose logs -f backend

# Debug with breakpoints
cd apps/backend
python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m uvicorn app.main:app --reload
```

### Frontend Debugging

- Use browser dev tools
- Next.js debugging: Set `NODE_OPTIONS='--inspect'`
- React DevTools browser extension

### Common Issues

**Port conflicts:**
```bash
# Check what's using ports
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL
```

**Docker issues:**
```bash
# Reset Docker environment
make clean
make dev-up
```

**Package conflicts:**
```bash
# Clear node_modules and reinstall
pnpm clean-modules
make install-all
```

## 🎨 Code Style

### Formatting & Linting

All code is automatically formatted and linted:

```bash
# Format code
pnpm run format        # TypeScript
cd apps/backend && black .  # Python

# Lint code
make lint-all

# Type checking
pnpm type-check
```

### Conventions

- **Commits**: Use conventional commits (`feat:`, `fix:`, `docs:`)
- **Naming**: Use camelCase (TS) and snake_case (Python)
- **Files**: Use kebab-case for files and directories
- **Branches**: `feature/description`, `fix/description`, `docs/description`

## 🚢 Deployment

See [Deployment Guide](deployment.md) for production deployment instructions.

For development deployment testing:

```bash
# Build all applications
pnpm build

# Test Docker builds
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build
```

## 📚 Additional Resources

- [API Reference](api-reference.md)
- [System Architecture](architecture.md)
- [External APIs Guide](external-apis.md)
- [Troubleshooting](troubleshooting.md)