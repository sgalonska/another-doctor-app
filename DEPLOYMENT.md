# Another Doctor - Deployment Guide

## Overview

The Another Doctor application is now deployed using **Render**, a modern cloud platform that provides simplified deployment, automatic scaling, and managed databases.

## Quick Deployment

1. **Run the deployment script:**
   ```bash
   ./scripts/deploy-render.sh
   ```

2. **Complete setup in Render Dashboard:**
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Connect your GitHub repository
   - Use the Blueprint deployment with `render.yaml`

## Architecture

```
Frontend (Next.js) → Backend (FastAPI) → PostgreSQL Database
       ↓                    ↓                    ↓
  Render Web Service   Render Web Service   Render Managed DB
                            ↓
                       Redis Cache
                         ↓
                   Render Managed DB
```

## Services Created

- **Frontend**: Next.js web service at `app.another.doctor`
- **Backend**: FastAPI web service at `api.another.doctor`
- **Database**: PostgreSQL 15 managed database
- **Cache**: Redis managed database

## Cost

**Estimated Monthly Cost: $28**
- 4 services × $7/month (Starter plan)

## Features

✅ **Zero DevOps** - Automatic deployments from Git  
✅ **Auto-scaling** - Scales based on traffic  
✅ **SSL Certificates** - Free SSL for custom domains  
✅ **Managed Databases** - PostgreSQL and Redis with backups  
✅ **Built-in Monitoring** - Logs, metrics, and alerting  
✅ **Easy Configuration** - Environment variables via dashboard

## Documentation

- **Complete Guide**: [`docs/RENDER_DEPLOYMENT_GUIDE.md`](./docs/RENDER_DEPLOYMENT_GUIDE.md)
- **Quick Start**: [`scripts/deploy-instructions.md`](./scripts/deploy-instructions.md)

## Migration from GCP

This project was previously deployed on Google Cloud Platform but has been migrated to Render for:

- **Simplified deployment process**
- **Reduced operational complexity**
- **Predictable pricing**
- **Better developer experience**

The GCP infrastructure files have been removed. The backup is available at `docs/GCP_DEPLOYMENT_GUIDE.md.backup` if needed.

## Support

For deployment issues:
1. Check the [Render documentation](https://render.com/docs)
2. Review service logs in the Render dashboard
3. Consult the troubleshooting section in the deployment guide