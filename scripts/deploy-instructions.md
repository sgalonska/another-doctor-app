# Another Doctor - Render Deployment Instructions

This application has been migrated from Google Cloud Platform to Render for simplified deployment and management.

## Quick Start

Run the deployment script:

```bash
./scripts/deploy-render.sh
```

## Manual Deployment Steps

### Step 1: Connect Repository to Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Sign up/Login and connect your GitHub account
3. Click "New +" → "Blueprint"
4. Select your "another-doctor-app" repository
5. Render will automatically read `render.yaml` and create all services

### Step 2: Configure Environment Variables

**Backend Service:**
- Set `STRIPE_SECRET_KEY` in the backend service environment variables

**Frontend Service:**  
- Set `STRIPE_SECRET_KEY` in the frontend service environment variables

### Step 3: Configure Custom Domains

**Backend API Domain** (`api.another.doctor`):
1. Go to backend service → Settings → Custom Domains
2. Add `api.another.doctor`

**Frontend Domain** (`app.another.doctor`):
1. Go to frontend service → Settings → Custom Domains  
2. Add `app.another.doctor`

### Step 4: Configure DNS

In **Cloudflare DNS**, add these CNAME records:

| Type | Name | Target |
|------|------|--------|
| CNAME | app | `another-doctor-frontend.onrender.com` |
| CNAME | api | `another-doctor-backend.onrender.com` |

## Services Created

The deployment creates these services:

- **Frontend**: Next.js web service with custom domain
- **Backend**: FastAPI web service with custom domain  
- **Database**: PostgreSQL managed database
- **Cache**: Redis managed database

## Summary

After deployment:
- ✅ Frontend: `https://app.another.doctor`
- ✅ Backend: `https://api.another.doctor`
- ✅ SSL automatically provisioned by Render
- ✅ Automatic scaling and zero-downtime deployments
- ✅ Built-in monitoring and logging

**Estimated Cost**: $28/month (4 × $7 starter services)

## Troubleshooting

**Services not starting:**
- Check build logs in Render dashboard
- Verify environment variables are set correctly
- Ensure `requirements.txt` and `package.json` are up to date

**Domain not working:**
- Verify CNAME records in Cloudflare DNS
- Wait up to 24 hours for SSL certificate provisioning
- Check service status in Render dashboard

## Monitoring

- **Render Dashboard**: https://dashboard.render.com
- **Service Logs**: Available in each service's dashboard
- **Metrics**: CPU, memory, and request metrics built-in

## Documentation

For detailed deployment information, see:
- `./docs/RENDER_DEPLOYMENT_GUIDE.md`