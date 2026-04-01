#!/bin/bash
set -e

# Frontend Deployment Script
# This script builds and deploys the Next.js frontend to Cloud Run

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/final-frontend-llmops"

# Default values
PROJECT_ID="${PROJECT_ID:-search-ahmed}"
REGION="${REGION:-us-central1}"
ENVIRONMENT="${ENVIRONMENT:-dev}"
BACKEND_URL="${BACKEND_URL:-https://llmops-backend-dev-oxigyhdstq-uc.a.run.app}"

echo "========================================="
echo "Frontend Deployment"
echo "========================================="
echo "Project:      $PROJECT_ID"
echo "Region:       $REGION"
echo "Environment:  $ENVIRONMENT"
echo "Backend URL:  $BACKEND_URL"
echo "========================================="
echo ""

# Step 1: Build and push Docker image
echo "📦 Building frontend Docker image..."
cd "$FRONTEND_DIR"

IMAGE_TAG="$(git rev-parse --short HEAD)"
IMAGE_URI="us-central1-docker.pkg.dev/$PROJECT_ID/llmops-repo/llmops-frontend:$IMAGE_TAG"

gcloud builds submit \
  --project="$PROJECT_ID" \
  --config=cloudbuild.yaml \
  --substitutions="_BACKEND_URL=$BACKEND_URL,_IMAGE_URI=$IMAGE_URI,_SERVICE_NAME=llmops-frontend-$ENVIRONMENT"

echo "✅ Image built and pushed: $IMAGE_URI"
echo ""

# Step 2: Deploy with Terraform
echo "🚀 Deploying to Cloud Run with Terraform..."
cd "$SCRIPT_DIR/main"

terraform init -backend-config="bucket=search-ahmed-tf-state"

terraform apply \
  -var-file="${ENVIRONMENT}.tfvars" \
  -var="docker_image=$IMAGE_URI" \
  -var="backend_url=$BACKEND_URL" \
  -auto-approve

# Get frontend URL
FRONTEND_URL=$(terraform output -raw frontend_url)

echo ""
echo "========================================="
echo "✅ Frontend deployed successfully!"
echo "========================================="
echo "Frontend URL: $FRONTEND_URL"
echo ""
echo "⚠️  NEXT STEP: Update backend CORS"
echo "Add this URL to backend's ALLOW_ORIGINS:"
echo ""
echo "  terraform apply \\"
echo "    -var='additional_allowed_origins=[\"$FRONTEND_URL\"]' \\"
echo "    -var-file=dev.tfvars"
echo ""
echo "Or set in terraform.tfvars:"
echo "  additional_allowed_origins = [\"$FRONTEND_URL\"]"
echo "========================================="
