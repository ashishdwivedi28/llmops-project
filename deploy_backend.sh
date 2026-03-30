gcloud run deploy llmops-backend \
  --source ./xyz \
  --region us-central1 \
  --project search-ahmed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=search-ahmed,GOOGLE_CLOUD_LOCATION=us-central1,BIGQUERY_PROJECT=search-ahmed,FIRESTORE_PROJECT=search-ahmed,RAG_LOCATION=us-central1,LOG_LEVEL=INFO,HOST=0.0.0.0 \
  --quiet
