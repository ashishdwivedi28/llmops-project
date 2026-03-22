# CLOUD_SETUP.md
# Complete Step-by-Step Guide: GitHub → GCP → Live Application
# Tailored for: Vertex AI (ADC) Backend + Next.js Frontend + Terraform Infra + Workload Identity Federation

---

## PREREQUISITES

Install these on your laptop before starting:
- Google Cloud SDK: https://cloud.google.com/sdk/docs/install
- Terraform: https://developer.hashicorp.com/terraform/install
- Git: https://git-scm.com/downloads
- Docker Desktop: https://www.docker.com/products/docker-desktop

---

## PHASE 1: GOOGLE CLOUD PROJECT SETUP (10 minutes)

### Step 1.1 — Create or select your GCP project

Open Google Cloud Console: https://console.cloud.google.com

If creating new project:
1. Click the project dropdown at the top
2. Click "New Project"
3. Name: llmops-pipeline
4. Note your Project ID (e.g. llmops-pipeline-123456)

If using existing project:
1. Note your Project ID from the dashboard

### Step 1.2 — Set your project in gcloud CLI

Open your terminal:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud config set compute/region us-central1
```

Replace YOUR_PROJECT_ID with your actual project ID.

### Step 1.3 — Enable billing

1. Go to: https://console.cloud.google.com/billing
2. Link a billing account to your project
3. Cloud Run free tier = 2 million requests/month — you will NOT be charged for dev usage

### Step 1.4 — Run Terraform to create all resources

```bash
cd infra/

terraform init

terraform plan -var="project_id=YOUR_PROJECT_ID" -var="github_repo=YOUR_GITHUB_USERNAME/YOUR_REPO_NAME"

terraform apply \
  -var="project_id=project-3e17312f-26d8-4511-821" \
  -var="github_repo=ashishdwivedi28/llmops-project"
```

**IMPORTANT:** Replace `YOUR_GITHUB_USERNAME/YOUR_REPO_NAME` with your actual repo (e.g., `ashish-s-dimri/llmops-pipeline`).

Type "yes" when prompted.

This creates:
- Artifact Registry (Docker image storage)
- Secret Manager secrets (for API keys)
- Service account for GitHub Actions (`github-actions-deploy`)
- Service account for Backend Runtime (`llmops-backend-sa`)
- **Workload Identity Federation Pool & Provider** (Secure authentication without keys)
- All required IAM permissions

Note the outputs printed at the end:
- `artifact_registry_url`
- `github_sa_email`
- `backend_sa_email`
- `workload_identity_provider` → **You will need this for GitHub Secrets**

### Step 1.5 — Add your API keys to Secret Manager

We use Vertex AI (Gemini) which uses IAM (no key needed), but Claude still needs a key.

```bash
# Add Anthropic API key (optional — only if you use Claude)
echo -n "YOUR_ACTUAL_ANTHROPIC_API_KEY" | \
  gcloud secrets versions add ANTHROPIC_API_KEY --data-file=-
```

---

## PHASE 2: GITHUB REPOSITORY SETUP (10 minutes)

### Step 2.1 — Push your code (if not done already)

You have already pushed your code to GitHub. Ensure your repository is private if possible.

### Step 2.2 — Add GitHub Repository Secrets

Go to your GitHub repo → Settings → Secrets and variables → Actions → New repository secret

Add these secrets one by one:

**Secret 1:**
  *   **Name:** `GCP_PROJECT_ID`
  *   **Value:** `your-actual-project-id`

**Secret 2:**
  *   **Name:** `GCP_SA_EMAIL`
  *   **Value:** (Copy `github_sa_email` from Terraform output. e.g. `github-actions-deploy@...`)

**Secret 3:**
  *   **Name:** `GCP_WORKLOAD_IDENTITY_PROVIDER`
  *   **Value:** (Copy `workload_identity_provider` from Terraform output. e.g. `projects/123456/locations/global/workloadIdentityPools/...`)

**Secret 4:**
  *   **Name:** `BACKEND_URL`
  *   **Value:** (Leave empty for now — you'll fill this after backend deploys)

**Done! No JSON keys required.**

---

## PHASE 3: DEPLOYMENT (Automated via GitHub Actions)

Since we have set up the `.github/workflows/backend-deploy.yml` and secrets, you can trigger a deployment by pushing to the `main` branch.

### Step 3.1 — Trigger Backend Deployment

```bash
# Make a small change to trigger CI/CD if needed, or just ensure latest is pushed
git push origin main
```

Go to GitHub → Actions tab.
You should see "Backend — Build and Deploy" running.
Watch it complete. It will print the Backend URL at the end of the logs.

### Step 3.2 — Update GitHub secret with backend URL

Copy the URL from the GitHub Action logs (e.g., `https://llmops-backend-xxxx-el.a.run.app`).
Go to GitHub repo → Settings → Secrets → BACKEND_URL
Update value to: `https://llmops-backend-xxxx-el.a.run.app`
(no trailing slash)

### Step 3.3 — Deploy Frontend

The frontend deployment is also automated via GitHub Actions, but it needs the `BACKEND_URL` secret we just set.

1.  After setting `BACKEND_URL` in Step 3.2...
2.  Go to GitHub Actions tab.
3.  Select "Frontend — Build and Deploy" workflow.
4.  Click "Run workflow" (or push a change to `final-frontend-llmops/` folder).

Wait for deployment. The Action logs will show the Frontend URL.
Open that URL in your browser.

---

## PHASE 4: CONFIGURE BACKEND CORS FOR PRODUCTION

Now that you have the frontend URL, update CORS in the backend service so the frontend can talk to it.

```bash
FRONTEND_URL="https://llmops-frontend-xxxx-el.a.run.app" # REPLACE THIS

gcloud run services update llmops-backend \
  --region us-central1 \
  --update-env-vars=ALLOWED_ORIGINS="$FRONTEND_URL,http://localhost:3000"
```

---

## PHASE 5: VERIFICATION

1.  **Mock App**: Go to your frontend URL -> Chat -> Select "Mock App". Send "Hello". It should reply instantly.
2.  **General Bot**: Select "General Assistant". Send "Who are you?". It should use **Vertex AI (Gemini)** to reply.
    *   *Note: This works because the backend is running as `llmops-backend-sa`, which Terraform granted `roles/aiplatform.user`.*
3.  **RAG Bot**: Select "RAG Bot". Send "What is RAG?". It should reply using the mock vector store content.

---

## COST ESTIMATE (your usage level)

Cloud Run:       $0/month   (free tier: 2M requests/month)
Artifact Registry: ~$0.10/month  (image storage)
Secret Manager:  $0.06/month  (6 secret versions)
Vertex AI:       Pay per character (Gemini Flash is very cheap)

Total estimate for development/demo: Under $5/month

---

## TROUBLESHOOTING

**Problem:** GitHub Actions fails with "Permission denied" during authentication.
**Fix:**
1. Check that `GCP_WORKLOAD_IDENTITY_PROVIDER` secret matches the Terraform output exactly.
2. Check that `GCP_SA_EMAIL` secret matches the Terraform output.
3. Ensure the Terraform variable `github_repo` was set correctly to `username/repo` (case sensitive). If you need to change it:
   ```bash
   terraform apply -var="project_id=..." -var="github_repo=CorrectUser/CorrectRepo"
   ```

**Problem:** Backend returns 500 or "Gemini call failed"
**Fix:** Check Cloud Run logs: `gcloud beta run services logs tail llmops-backend`.
    *   If it says "Service account not found", ensure `llmops-backend-sa` exists.
    *   If it says "Permission denied" for Vertex AI, ensure `llmops-backend-sa` has `roles/aiplatform.user`.

**Problem:** Frontend shows "Backend unreachable"
**Fix:** Check CORS settings on the backend. Ensure the frontend URL is in `ALLOWED_ORIGINS`.