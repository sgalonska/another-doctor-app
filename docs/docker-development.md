# Docker Development Environment

Complete local development environment for Another Doctor using Docker containers.

## 🎯 Overview

This setup provides a complete local development environment that mirrors production, allowing you to run everything locally except for LLM services (which would require external APIs).

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
         │   Port: 5432    │   Port: 6379    │   Port: 6333    │
         └─────────────────┴─────────────────┴─────────────────┘
                                 │
         ┌───────────────────────────────────────────────────────┐
         │                   Storage                             │
         ├─────────────────┬─────────────────────────────────────┤
         │      MinIO      │           Development Tools         │
         │  Ports: 9000    │   PgAdmin, Redis Commander,        │
         │         9001    │   Prometheus, Grafana               │
         └─────────────────┴─────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Docker**: Version 20.0+
- **Docker Compose**: Version 2.0+
- **Git**: Latest version
- **8GB RAM minimum** (recommended 16GB)

### Start Development Environment

```bash
# Start core services
make dev-up

# Or start with development tools
make dev-up-tools

# Or start with seed data
make dev-up-seed
```

### Access Services

Once started, access these services in your browser:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | - |
| **Backend API** | http://localhost:8000 | - |
| **API Docs** | http://localhost:8000/docs | - |
| **MinIO Console** | http://localhost:9001 | minioadmin/minioadmin |
| **PgAdmin** | http://localhost:5050 | admin@anotherdoctor.local/admin |
| **Redis Commander** | http://localhost:8081 | - |
| **Qdrant Dashboard** | http://localhost:6333/dashboard | - |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3001 | admin/admin |

## 📋 Available Services

### Core Services (Always Running)

- **PostgreSQL** - Main database
- **Redis** - Cache and job queue
- **Qdrant** - Vector database for embeddings
- **MinIO** - S3-compatible file storage
- **Backend** - FastAPI application
- **Frontend** - Next.js application
- **Workers** - Background job processors

### Development Tools (Optional)

- **PgAdmin** - PostgreSQL administration
- **Redis Commander** - Redis administration
- **Prometheus** - Metrics collection
- **Grafana** - Metrics visualization

## 🔧 Development Commands

### Environment Management

```bash
# Start development environment
make dev-up                    # Core services only
make dev-up-tools             # With admin tools
make dev-up-seed              # With sample data

# Stop services
make dev-down                 # Graceful shutdown
./scripts/dev-stop.sh --clean # Remove all data

# Reset environment
make dev-reset                # Complete reset
```

### Logs and Monitoring

```bash
# View logs
make dev-logs SERVICE=backend     # Specific service
./scripts/dev-logs.sh all        # All services
./scripts/dev-logs.sh backend -f # Follow backend logs

# Check service status
docker-compose ps
docker-compose ps --services --filter "status=running"
```

### Database Operations

```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d another_doctor

# Run migrations
docker-compose exec backend alembic upgrade head

# Create migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Seed development data
docker-compose -f docker-compose.yml -f docker-compose.dev.yml run --rm db-seed
```

### Service Interaction

```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell (if needed)
docker-compose exec frontend sh

# Worker shell
docker-compose exec workers bash

# Redis CLI
docker-compose exec redis redis-cli

# Direct database queries
docker-compose exec postgres psql -U postgres -d another_doctor -c "SELECT COUNT(*) FROM doctor;"
```

## 🧪 Testing

### Run Tests

```bash
# Backend tests
docker-compose exec backend python -m pytest

# Frontend tests (when container is running)
docker-compose exec frontend npm test

# Integration tests
docker-compose exec backend python -m pytest tests/integration/
```

### API Testing

```bash
# Health checks
curl http://localhost:8000/health
curl http://localhost:3000/api/health

# Test API endpoints
curl -X POST http://localhost:8000/api/v1/upload/text \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text_content=Patient has critical limb ischemia in left foot"

# Test file upload
curl -X POST http://localhost:8000/api/v1/upload/presigned-url \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "filename=test.pdf&content_type=application/pdf"
```

## 💾 Data Persistence

### Volume Mounts

Development data is persisted in Docker volumes:

- `postgres_data` - Database data
- `redis_data` - Redis persistence
- `qdrant_data` - Vector database
- `minio_data` - File storage
- `grafana_data` - Grafana dashboards
- `prometheus_data` - Metrics history

### Backup and Restore

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres another_doctor > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U postgres -d another_doctor

# Export volumes
docker run --rm -v another-doctor-app_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Import volumes
docker run --rm -v another-doctor-app_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /data
```

## 🔒 Security Notes

### Development Security

- All services use default development credentials
- **Never use these credentials in production**
- Services are exposed on localhost only
- No external network access by default

### Credentials Summary

| Service | Username | Password |
|---------|----------|----------|
| PostgreSQL | postgres | password |
| MinIO | minioadmin | minioadmin |
| PgAdmin | admin@anotherdoctor.local | admin |
| Grafana | admin | admin |

## 🐛 Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Check what's using ports
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL

# Stop conflicting services
sudo service postgresql stop  # If system PostgreSQL is running
```

**Services won't start:**
```bash
# Check Docker resources
docker system df
docker system prune -f

# Restart Docker daemon
# On macOS: Docker Desktop → Restart
# On Linux: sudo systemctl restart docker
```

**Database connection issues:**
```bash
# Check PostgreSQL is ready
docker-compose exec postgres pg_isready -U postgres

# Check backend can connect
docker-compose exec backend python -c "
from app.db.session import get_db
next(get_db())
print('Database connection successful')
"
```

**Frontend won't load:**
```bash
# Check Next.js build
docker-compose logs frontend

# Rebuild frontend container
docker-compose up --build frontend
```

**Volume permission issues:**
```bash
# Fix volume permissions (Linux/macOS)
docker-compose exec backend chown -R appuser:appuser /app
docker-compose restart backend
```

### Performance Issues

**Slow startup:**
- Increase Docker memory allocation (8GB recommended)
- Use SSD storage for Docker volumes
- Close unnecessary applications

**High resource usage:**
```bash
# Stop optional services
docker-compose stop prometheus grafana pgadmin redis-commander

# Use fewer worker processes
docker-compose up --scale workers=1
```

### Log Analysis

```bash
# Check all container logs
docker-compose logs

# Filter logs by service and time
docker-compose logs --since 10m backend

# Follow logs from multiple services
docker-compose logs -f backend workers

# Export logs
docker-compose logs backend > backend.log
```

## 🔄 Development Workflow

### Typical Development Session

1. **Start environment:**
   ```bash
   make dev-up
   ```

2. **Check health:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:3000
   ```

3. **Make changes:**
   - Edit code in `apps/backend/` or `apps/frontend/`
   - Changes are automatically reflected (hot reload)

4. **Test changes:**
   ```bash
   # Backend tests
   docker-compose exec backend python -m pytest
   
   # Frontend tests
   docker-compose exec frontend npm test
   ```

5. **View logs:**
   ```bash
   make dev-logs SERVICE=backend
   ```

6. **Stop when done:**
   ```bash
   make dev-down
   ```

### Code Changes

- **Backend**: Auto-reload enabled, changes reflect immediately
- **Frontend**: Hot module replacement, changes reflect in browser
- **Packages**: Restart services after changes to shared packages
- **Docker configs**: Run `docker-compose up --build` after changes

## 📚 Additional Resources

- [Development Guide](development.md)
- [API Reference](api-reference.md)
- [Deployment Guide](deployment.md)
- [Troubleshooting Guide](troubleshooting.md)