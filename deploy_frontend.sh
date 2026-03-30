cd final-frontend-llmops
gcloud run deploy llmops-frontend \
  --source . \
  --region us-central1 \
  --project search-ahmed \
  --allow-unauthenticated \
  --set-env-vars NEXT_PUBLIC_API_URL=https://llmops-backend-36231825761.us-central1.run.app \
  --quiet
