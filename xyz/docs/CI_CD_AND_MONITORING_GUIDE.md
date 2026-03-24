# CI/CD & End-to-End Monitoring Guide

This guide explains how to transition from manual scripts to full automation using **GitHub Actions**, how to run the app locally while connected to the cloud, and how to verify the entire system is working.

---

## 1. Setting up GitHub Actions (CI/CD)

Instead of running `./scripts/deploy_backend.sh` manually, we can let GitHub deploy every time you push code.

### Prerequisites (One-Time Setup)

You need to add "Secrets" to your GitHub Repository settings (**Settings > Secrets and variables > Actions**).

| Secret Name | Value | Description |
| :--- | :--- | :--- |
| `GCP_PROJECT_ID` | `your-project-id` | Your Google Cloud Project ID. |
| `GCP_SA_EMAIL` | *(See Below)* | Email of the `github-actions-deploy` Service Account. |
| `GCP_WORKLOAD_IDENTITY_PROVIDER` | *(See Below)* | The full resource name of the WIF Provider. |

### How to get these values?

Run these commands in your terminal (since you already ran Terraform):

```bash
# Get Service Account Email
cd infra
terraform output github_sa_email
# Output example: github-actions-deploy@project-id.iam.gserviceaccount.com

# Get Workload Identity Provider
terraform output workload_identity_provider
# Output example: projects/123456789/locations/global/workloadIdentityPools/github-actions-pool/providers/github-actions-provider
```

### The Workflows

We have created three workflows in `.github/workflows/`:
1.  **`backend-deploy.yml`**: Deploys the FastAPI backend to Cloud Run when `xyz/` changes.
2.  **`trigger-deploy.yml`**: Deploys the Trigger Service to Cloud Run when `xyz/trigger_service/` changes.
3.  **`frontend-deploy.yml`**: Deploys the Next.js frontend (configure `BACKEND_URL` secret for this).

**To Trigger:** Simply push changes to the `main` branch.
```bash
git add .
git commit -m "Enable CI/CD"
git push origin main
```

---

## 2. Running Locally (Connected to Cloud)

You can run the FastAPI backend on your laptop but have it talk to the **real** BigQuery, Firestore, and Vertex AI in the cloud.

### Step 1: Authentication

Your local code needs permission to access GCP.
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### Step 2: Environment Variables

Create a `.env` file in `xyz/` (or update existing):

```ini
GOOGLE_CLOUD_PROJECT=your-project-id
BIGQUERY_PROJECT=your-project-id
FIRESTORE_PROJECT=your-project-id
RAG_LOCATION=us-central1
GCS_BUCKET_DOCS=your-project-id-llmops-docs
PIPELINE_ROOT_GCS=gs://your-project-id-llmops-pipeline-artifacts
```

### Step 3: Run Server

```bash
cd xyz
uvicorn app.main:app --reload --port 8000
```

Now, when you hit `http://localhost:8000/invoke`, it writes logs to the **real** BigQuery in the cloud!

---

## 3. Verifying the End-to-End Pipeline

Here is how to "see" every part of the system working.

### A. The Serving Loop (Chat)

1.  **Action**: Send a request.
    ```bash
    curl -X POST http://localhost:8000/invoke \
      -H "Content-Type: application/json" \
      -d '{"app_id": "default_llm", "user_input": "Test query"}'
    ```
2.  **Verification**: Go to **BigQuery Console**.
    *   Query: `SELECT * FROM llmops.requests ORDER BY timestamp DESC LIMIT 1`
    *   *Success*: You see your "Test query" and the model's response.

### B. The RAG Loop (Ingestion)

1.  **Action**: Upload a file.
    ```bash
    echo "This is a test document." > test.txt
    gsutil cp test.txt gs://YOUR_PROJECT_ID-llmops-docs/rag_bot/test.txt
    ```
2.  **Verification 1**: Go to **Cloud Run Console** -> `llmops-trigger` -> **Logs**.
    *   *Success*: Log entry saying `GCS upload detected: ... submitted pipeline ...`
3.  **Verification 2**: Go to **Vertex AI > Pipelines**.
    *   *Success*: You see a `rag-ingestion` pipeline in "Running" or "Succeeded" state.

### C. The Improvement Loop (Evaluation)

1.  **Action**: Trigger manually (since you don't want to wait for 2 AM).
    ```bash
    # From your local terminal
    python pipelines/evaluation_pipeline.py --project YOUR_PROJECT_ID --submit --app_id default_llm
    ```
2.  **Verification 1**: Go to **Vertex AI > Pipelines**.
    *   *Success*: See `llmops-evaluation` pipeline running.
3.  **Verification 2**: Go to **BigQuery Console**.
    *   Query: `SELECT * FROM llmops.evaluation_results WHERE app_id='default_llm'`
    *   *Success*: You see scores (correctness, relevance) for your recent chats.

---

## 4. Monitoring Dashboard

To "see everything" in one place, use the **Google Cloud Console**:

1.  **Vertex AI Pipelines**: The visual source of truth for all automation.
    *   Green Checkmarks = Healthy automation.
    *   Red Exclamation = Something broke (click to see logs).

2.  **Cloud Run**: The health of your API.
    *   Check "Metrics" tab for Latency and Error Rate.

3.  **BigQuery**: The brain.
    *   All system state, logs, and scores are here.

---

## Summary

*   **Code Changes** -> **GitHub Actions** -> **Cloud Run** (Automatic)
*   **Local Run** -> **ADC (`gcloud auth`)** -> **Cloud Resources** (Development)
*   **Uploads/Schedules** -> **Trigger Service** -> **Vertex Pipelines** (Automation)
