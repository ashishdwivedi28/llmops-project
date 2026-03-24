#!/bin/bash
# Run this ONCE to connect GCS uploads to the RAG ingestion KFP pipeline.
# Requires: Cloud Run function that triggers Vertex AI Pipelines.

PROJECT_ID=$1
REGION=${2:-us-central1}
BUCKET_NAME=${3:-${PROJECT_ID}-llmops-docs}

if [ -z "$PROJECT_ID" ]; then
  echo "Usage: ./setup_gcs_trigger.sh YOUR_PROJECT_ID [REGION] [BUCKET_NAME]"
  exit 1
fi

echo "Setting up GCS → Pub/Sub → KFP trigger for project: $PROJECT_ID"

# 1. Create document bucket if it doesn't exist
# MANAGED BY TERRAFORM (infra/storage.tf)
# gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME/ 2>/dev/null || echo "Bucket exists."

# 2. Create Pub/Sub topic for GCS notifications
# MANAGED BY TERRAFORM (infra/pubsub.tf)
# gcloud pubsub topics create llmops-doc-uploads \
#   --project=$PROJECT_ID 2>/dev/null || echo "Topic exists."

# 3. Configure GCS to notify Pub/Sub on new uploads
# MANAGED BY TERRAFORM (infra/pubsub.tf)
# gsutil notification create \
#   -t projects/$PROJECT_ID/topics/llmops-doc-uploads \
#   -f json \
#   -e OBJECT_FINALIZE \
#   gs://$BUCKET_NAME

echo "GCS trigger configured via Terraform."
echo "Bucket: gs://$BUCKET_NAME"
echo "Pub/Sub topic: llmops-doc-uploads"
echo ""
echo "Next: Deploy the Cloud Function trigger (see scripts/deploy_trigger_function.sh)"
