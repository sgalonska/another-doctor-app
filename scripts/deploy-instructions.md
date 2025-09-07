# Another Doctor - Complete GCP Deployment Instructions

Your Docker images are built successfully! Now we just need to authenticate and push them. Follow these steps:

## Step 1: Authenticate with Google Cloud

```bash
# Authenticate (this will open browser)
gcloud auth login

# Set project
gcloud config set project another-doctor-471116

# Configure Docker authentication
gcloud auth configure-docker us-central1-docker.pkg.dev
```

## Step 2: Push Docker Images

Your images are already built. Just push them:

```bash
# Push frontend image
docker push us-central1-docker.pkg.dev/another-doctor-471116/another-doctor-prod-repo/frontend:latest

# Push backend image  
docker push us-central1-docker.pkg.dev/another-doctor-471116/another-doctor-prod-repo/backend:latest
```

## Step 3: Deploy Infrastructure

```bash
cd infra/gcp
terraform apply -var-file="environments/prod.tfvars" -auto-approve
```

## Step 4: Set Up Domain Mapping

After deployment, get your frontend service URL:

```bash
# Get frontend URL
gcloud run services describe another-doctor-prod-frontend \
    --platform=managed \
    --region=us-central1 \
    --format="value(status.url)"
```

Then create domain mapping:

```bash
# Create domain mapping
gcloud run domain-mappings create \
    --service=another-doctor-prod-frontend \
    --domain=app.another.doctor \
    --region=us-central1
```

## Step 5: Configure DNS

In **Cloudflare DNS**, add this CNAME record:
- **Name**: `app`
- **Target**: `ghs.googlehosted.com`

## Step 6: Verify Domain (if needed)

If Google requires domain verification:

1. Go to [Google Search Console](https://search.google.com/search-console)
2. Add `app.another.doctor` as a property
3. Verify ownership using DNS TXT record method

## Summary

After these steps:
- ✅ Frontend: `https://app.another.doctor`
- ✅ Backend: Available via Cloud Run URL 
- ✅ SSL automatically provisioned by Google
- ✅ Domain mapping complete

**Note**: DNS propagation can take 15-60 minutes after adding the CNAME record.

## Troubleshooting

If you get authentication errors:
```bash
# Re-authenticate
gcloud auth login
gcloud auth application-default login
```

If domain doesn't work after 1 hour:
1. Check CNAME record in Cloudflare
2. Verify domain ownership in Google Search Console
3. Check Cloud Run logs for errors

## Monitoring

- **Cloud Console**: https://console.cloud.google.com/run?project=another-doctor-471116
- **Logs**: https://console.cloud.google.com/logs/query?project=another-doctor-471116