# 🚀 Local Development Guide

This guide explains how to run Another Doctor locally using the new manual approach optimized for GCP deployment.

## 🏗️ Architecture Overview

- **Infrastructure Services**: PostgreSQL, Redis, Qdrant (Docker)
- **Application Services**: Frontend & Backend (Manual/CLI)
- **Cloud Storage**: GCP Cloud Storage (no local MinIO)

## ⚡ Quick Start

### 1. Start Infrastructure Services
```bash
make dev-manual
```

This starts the database and other infrastructure services in Docker.

### 2. Start Backend (Terminal 1)
```bash
./scripts/run-backend-local.sh
```

### 3. Start Frontend (Terminal 2) 
```bash
./scripts/run-frontend-local.sh
```

## 🌐 Access Your Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000  
- **API Docs:** http://localhost:8000/docs
- **Database:** localhost:5432 (postgres/password)
- **Redis:** localhost:6379
- **Qdrant:** http://localhost:6333

## 🛠️ Available Commands

### Infrastructure
```bash
make dev-up-infra          # Start only infrastructure services
make backend-manual        # Start backend manually  
make frontend-manual       # Start frontend manually
make dev-down             # Stop all services
```

### Individual Scripts
```bash
./scripts/run-backend-local.sh   # Backend with auto-reload
./scripts/run-frontend-local.sh  # Frontend with hot reload
```

## 🔧 Benefits of This Approach

### ✅ **Immediate Development**
- ✅ No Docker container build issues
- ✅ Direct CLI output and error messages  
- ✅ Hot reload for both frontend and backend
- ✅ Easy debugging with direct access to processes

### ✅ **GCP Ready**
- ✅ No MinIO/S3 dependencies
- ✅ Uses Google Cloud Storage configuration
- ✅ Matches production environment setup
- ✅ Simplified deployment pipeline

### ✅ **Better Developer Experience**
- ✅ Faster startup times
- ✅ Clear separation of infrastructure vs application
- ✅ Easy to run individual components
- ✅ Standard Python virtual environments and npm workflows

## 🐛 Troubleshooting

### Infrastructure Issues
```bash
# Check infrastructure status
docker-compose -f docker-compose.infrastructure.yml ps

# View logs
docker-compose -f docker-compose.infrastructure.yml logs postgres
docker-compose -f docker-compose.infrastructure.yml logs redis
docker-compose -f docker-compose.infrastructure.yml logs qdrant
```

### Backend Issues
- Check the terminal running `./scripts/run-backend-local.sh`
- Ensure database is running: `docker-compose -f docker-compose.infrastructure.yml ps`
- Check virtual environment: `source apps/backend/venv/bin/activate`

### Frontend Issues
- Check the terminal running `./scripts/run-frontend-local.sh`
- Clear node_modules if needed: `rm -rf node_modules && pnpm install`
- Check if pnpm is installed: `corepack enable`

## 🚀 Production Deployment

This setup mirrors the GCP production environment where:
- Database, Redis, Qdrant run as managed services
- Frontend and Backend run as separate services
- File storage uses GCP Cloud Storage

## 📝 Next Steps

1. **Development**: Use the manual scripts for active development
2. **Testing**: Run tests using the same infrastructure 
3. **Deployment**: Deploy to GCP using the existing infrastructure setup

---

💡 **Tip**: Keep one terminal for backend, one for frontend, and use your IDE for editing. This provides the best development experience!