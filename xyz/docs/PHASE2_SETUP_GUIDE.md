# PHASE 2 CLOUD SETUP & DEPLOYMENT GUIDE

This document provides a step-by-step guide to deploying the complete LLMOps platform to Google Cloud.
Follow these steps exactly to move from "local development" to "production cloud environment".

## 📋 Prerequisites
Ensure you have the following installed and authenticated:
- Google Cloud SDK (`gcloud`)
- Terraform
- Python 3.10+
- Docker

## 🛠️ Step 1: Infrastructure Provisioning (Terraform)
This step creates all physical resources: Cloud Run, BigQuery Tables, Service Accounts, and Storage Buckets.

1. **Navigate to the infra folder:**
   ```bash
   cd infra/
   ```

2. **Initialize Terraform:**
   ```bash
   terraform init
   ```

3. **Plan the deployment (Verify what will be created):**
   Replace `YOUR_PROJECT_ID` with your actual GCP Project ID.
   ```bash
   terraform plan -var="project_id=YOUR_PROJECT_ID"
   ```

4. **Apply the changes (Create resources):**
   ```bash
   terraform apply -var="project_id=YOUR_PROJECT_ID" -auto-approve
   ```

   **✅ Output to note:**
   - `backend_sa_email`: The email of the service account for the app.
   - `docs_bucket`: The bucket name for uploading documents.

---

## ⚙️ Step 2: Database & Config Setup
Now that the infrastructure exists, we need to populate the databases.

1. **Navigate to the backend folder:**
   ```bash
   cd ../xyz
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Enable Firestore (Native Mode):**
   *   Go to [GCP Console > Firestore](https://console.cloud.google.com/firestore).
   *   Click "Create Database".
   *   Select **Native Mode**.
   *   Select Location: `us-central1` (or your preferred region).
   *   Click "Create".

4. **Seed Firestore Configuration:**
   This pushes your local `config.json` logic into the live Firestore database.
   ```bash
   python scripts/seed_firestore_config.py --project YOUR_PROJECT_ID
   ```

---

## 🧠 Step 3: RAG Engine Setup (Vertex AI)
This creates the Vector Database (Corpus) for your documents.

1. **Create the RAG Corpus:**
   ```bash
   python scripts/setup_rag_corpus.py --project YOUR_PROJECT_ID --app_id rag_bot
   ```
   *   **Note:** This command will automatically update Firestore with the new `rag_corpus_id`.

---

## 🚀 Step 4: Deploy Backend Application
Now we deploy the FastAPI code to Cloud Run.

1. **Run the deployment script:**
   ```bash
   # Make script executable
   chmod +x scripts/deploy_backend.sh

   # Deploy
   ./scripts/deploy_backend.sh YOUR_PROJECT_ID us-central1
   ```

2. **Verify Deployment:**
   *   Go to [Cloud Run Console](https://console.cloud.google.com/run).
   *   Click on `llmops-backend`.
   *   Copy the **Service URL**.
   *   Test it:
       ```bash
       curl -X GET https://YOUR_SERVICE_URL/
       ```
       Expected output: `{"status": "ok", ...}`

---

## 🌐 Step 5: Frontend Deployment
1. **Navigate to frontend folder:**
   ```bash
   cd ../final-frontend-llmops
   ```

2. **Deploy to Cloud Run:**
   ```bash
   gcloud run deploy llmops-frontend \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars NEXT_PUBLIC_API_URL=https://YOUR_BACKEND_SERVICE_URL
   ```
   *(Replace `YOUR_BACKEND_SERVICE_URL` with the URL from Step 4)*

---

## 🤖 Step 6: Pipeline Automation (Vertex AI)
Finally, we compile and upload the KFP pipelines for automation.

1. **Compile Master Pipeline:**
   ```bash
   cd ../xyz
   export PYTHONPATH=$PYTHONPATH:.
   python pipelines/master_pipeline.py --project YOUR_PROJECT_ID --compile
   ```

2. **Submit a Test Run (Evaluation):**
   ```bash
   python pipelines/master_pipeline.py --project YOUR_PROJECT_ID --submit --trigger_type evaluation
   ```

---

## ✅ Verification Checklist
- [ ] **BigQuery:** Check `llmops.requests` table. Is it empty? (It should be until you make requests).
- [ ] **Firestore:** Check `configs` collection. Do you see `rag_bot`, `default_llm`?
- [ ] **Cloud Run:** Are both `llmops-backend` and `llmops-frontend` green?
- [ ] **Vertex AI:** Do you see a pipeline run in the "Pipelines" section?

You are now running a Production-Grade LLMOps Platform! 🚀
