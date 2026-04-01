# Frontend Deployment Guide

This guide explains how to deploy the **optional** Next.js frontend to Cloud Run.

## ⚠️ Important: Frontend is Optional

The LLMOps backend (`infra/advanced_deployment/`) is a **standalone production API** and does NOT require this frontend.

This frontend:
- ✅ Provides a web UI for testing/demos
- ✅ Can be deployed alongside the backend
- ✅ **Can be completely removed** when only the API is needed

## Quick Deploy

### Option 1: Automated Script (Recommended)

```bash
# Deploy frontend with defaults
./infra/frontend_deployment/deploy.sh

# Or with custom settings
PROJECT_ID=search-ahmed \
ENVIRONMENT=dev \
BACKEND_URL=https://llmops-backend-dev-oxigyhdstq-uc.a.run.app \
./infra/frontend_deployment/deploy.sh
```

The script will:
1. Build Docker image with Next.js app
2. Push to Artifact Registry
3. Deploy to Cloud Run with Terraform
4. Output the frontend URL

### Option 2: Manual Steps

#### 1. Build and Push Image

```bash
cd final-frontend-llmops

# Build using Cloud Build
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions="_BACKEND_URL=https://llmops-backend-dev-oxigyhdstq-uc.a.run.app"
```

#### 2. Deploy with Terraform

```bash
cd infra/frontend_deployment/main

# Initialize
terraform init -backend-config="bucket=search-ahmed-tf-state"

# Get the image URI from previous step
IMAGE_URI="us-central1-docker.pkg.dev/search-ahmed/llmops-repo/llmops-frontend:TAG"

# Deploy
terraform apply \
  -var-file=dev.tfvars \
  -var="docker_image=$IMAGE_URI" \
  -var="backend_url=https://llmops-backend-dev-oxigyhdstq-uc.a.run.app"

# Get frontend URL
terraform output frontend_url
```

#### 3. Update Backend CORS

After deployment, add the frontend URL to backend's allowed origins:

```bash
cd infra/advanced_deployment/main

# Get frontend URL from previous step
FRONTEND_URL="https://llmops-frontend-dev-HASH.run.app"

# Update backend to allow frontend
terraform apply \
  -var-file=dev.tfvars \
  -var="additional_allowed_origins=[\"$FRONTEND_URL\"]"
```

Or add to `dev.tfvars`:
```hcl
additional_allowed_origins = ["https://llmops-frontend-dev-HASH.run.app"]
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Public Internet                       │
└──────────────┬──────────────────────┬───────────────────┘
               │                      │
               │ (Optional)           │ (Core)
               ↓                      ↓
    ┌──────────────────┐   ┌──────────────────────┐
    │  Cloud Run       │   │  Cloud Run           │
    │  Frontend        │──→│  Backend (LLMOps)    │
    │  (Next.js)       │   │  (FastAPI + ADK)     │
    └──────────────────┘   └──────────┬───────────┘
                                      │
                           ┌──────────┼───────────┐
                           ↓          ↓           ↓
                      Cloud SQL  Vertex AI     GCS
```

## Configuration

### Frontend Environment Variables
- `NEXT_PUBLIC_API_URL` - Backend API URL (set at build time)
- `NODE_ENV` - Production mode

### Backend CORS Update
- `additional_allowed_origins` - List of frontend URLs to allow

## Removal

When you no longer need the frontend:

```bash
# 1. Destroy Cloud Run service
cd infra/frontend_deployment/main
terraform destroy -var-file=dev.tfvars

# 2. Remove infrastructure code (optional)
rm -rf infra/frontend_deployment/

# 3. Remove frontend code (optional)
rm -rf final-frontend-llmops/
```

**The backend will continue working independently.**

## Development vs Production

### Local Development
```bash
# Terminal 1: Proxy to Cloud Run backend
gcloud run services proxy llmops-backend-dev \
  --region=us-central1 \
  --project=search-ahmed \
  --port=8080

# Terminal 2: Run frontend locally
cd final-frontend-llmops
pnpm run dev

# Access: http://localhost:3000
```

### Production Deployment
```bash
# Deploy frontend to Cloud Run
./infra/frontend_deployment/deploy.sh

# Access: https://llmops-frontend-dev-HASH.run.app
```

## Troubleshooting

### CORS Errors
**Symptom:** "Failed to fetch" errors in browser console

**Fix:** Ensure backend's `additional_allowed_origins` includes the frontend URL:
```bash
terraform apply \
  -var='additional_allowed_origins=["https://llmops-frontend-dev-HASH.run.app"]' \
  -var-file=dev.tfvars
```

### Image Build Failures
**Symptom:** Cloud Build fails

**Fix:** Ensure Artifact Registry repository exists:
```bash
gcloud artifacts repositories create llmops-repo \
  --repository-format=docker \
  --location=us-central1 \
  --project=search-ahmed
```

### Standalone Output Not Working
**Symptom:** Docker build fails with missing files

**Fix:** Ensure `next.config.ts` has:
```typescript
output: "standalone"
```

## Cost Optimization

Frontend Cloud Run service costs:
- **No traffic:** ~$0/month (pay-per-use)
- **Light usage:** ~$1-5/month
- **Moderate usage:** ~$10-20/month

To minimize costs:
- Use Cloud Run's CPU idle billing
- Set max instances limit
- Use CDN for static assets (future enhancement)

## Next Steps

After deployment:
1. Test the frontend at the Cloud Run URL
2. Add custom domain (optional)
3. Enable Cloud CDN (optional)
4. Add authentication (optional)

See `infra/frontend_deployment/README.md` for more details.
