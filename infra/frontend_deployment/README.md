# Frontend Deployment (Optional UI)

This directory contains the **optional frontend deployment** for the LLMOps Pipeline. The frontend provides a web UI for testing and interacting with the backend API.

## ⚠️ Important Note

**This frontend is NOT part of the core LLMOps pipeline.** The backend (`infra/advanced_deployment/`) can function independently as a production-ready LLMOps API.

This frontend deployment can be:
- ✅ Used for development/testing
- ✅ Deployed for demo purposes
- ❌ **Deleted entirely** when you only need the API

## Architecture

```
Internet → Cloud Run Frontend (Next.js)
               ↓
           Cloud Run Backend (FastAPI LLMOps Pipeline)
               ↓
           Cloud SQL + Vertex AI + GCS
```

## Deployment

### Prerequisites
- Backend already deployed (`infra/advanced_deployment/`)
- Docker image built and pushed to Artifact Registry

### Manual Deployment

```bash
cd infra/frontend_deployment/main

# Initialize
terraform init -backend-config="bucket=search-ahmed-tf-state"

# Plan
terraform plan \
  -var-file=dev.tfvars \
  -var="docker_image=us-central1-docker.pkg.dev/search-ahmed/llmops-repo/llmops-frontend:latest" \
  -var="backend_url=https://llmops-backend-dev-oxigyhdstq-uc.a.run.app"

# Apply
terraform apply \
  -var-file=dev.tfvars \
  -var="docker_image=us-central1-docker.pkg.dev/search-ahmed/llmops-repo/llmops-frontend:latest" \
  -var="backend_url=https://llmops-backend-dev-oxigyhdstq-uc.a.run.app"
```

### Build Frontend Image

```bash
# Navigate to frontend directory
cd final-frontend-llmops

# Build and push
gcloud builds submit \
  --config cloudbuild.yaml \
  --substitutions=_BACKEND_URL=https://llmops-backend-dev-oxigyhdstq-uc.a.run.app
```

## Removal

When you no longer need the frontend UI:

```bash
# Destroy Cloud Run service
cd infra/frontend_deployment/main
terraform destroy -var-file=dev.tfvars

# Delete this entire directory
rm -rf infra/frontend_deployment/

# Remove frontend code
rm -rf final-frontend-llmops/
```

The backend will continue working independently.

## Configuration

- **Port**: 3000
- **Public Access**: Enabled (allUsers can invoke)
- **Backend URL**: Configured via `NEXT_PUBLIC_API_URL` environment variable
- **CORS**: Backend must allow frontend URL in `ALLOW_ORIGINS`
