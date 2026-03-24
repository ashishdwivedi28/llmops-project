# Agent & Automation Pipelines Guide (Run C & D)

This document details the implementation of the **AI Agent** (powered by Google ADK) and the **Automation Pipelines** (powered by Vertex AI Pipelines / Kubeflow).

---

## Part 1: The ADK Agent (Run C)

### Overview
We upgraded the `AgentPipeline` to use the **Google Agent Development Kit (ADK)**. Instead of a simple hardcoded loop, the agent now uses a **ReAct (Reasoning + Acting)** framework to intelligently select tools to answer complex user queries.

### Architecture
*   **Core Logic**: `xyz/app/pipelines/agent_pipeline.py`
*   **Framework**: Google ADK (manages the "Think → Act → Observe" loop).
*   **Fallback**: If ADK fails or is unconfigured, it falls back to a standard LLM call.

### Implemented Tools
The agent has access to three specific tools:
1.  **`bigquery_query(sql)`**: Executes READ-ONLY `SELECT` queries against your BigQuery dataset. Useful for data analysis questions.
2.  **`list_gcs_files(bucket, prefix)`**: Lists files in a Google Cloud Storage bucket. Useful for finding documents.
3.  **`calculate(expression)`**: A safe mathematical calculator for precise arithmetic (which LLMs often struggle with).

### Configuration
To use this agent for a specific app (e.g., `data_agent`), update its config in Firestore:
```json
{
  "pipeline": "agent",
  "model": "gemini-2.0-flash",
  "system_prompt": "You are a helpful data assistant. Use tools to find information.",
  "max_iterations": 5
}
```

---

## Part 2: Automation Pipelines (Run D)

### Overview
We implemented three **Kubeflow Pipelines (KFP)** designed to run on **Vertex AI Pipelines**. These handle backend operations asynchronously, separating heavy lifting from the real-time API.

### 1. RAG Ingestion Pipeline
*   **File**: `xyz/pipelines/rag_ingestion_pipeline.py`
*   **Trigger**: GCS File Upload (via Eventarc/PubSub).
*   **Function**:
    1.  Reads a file uploaded to GCS.
    2.  Ingests it into the Vertex AI RAG Corpus.
    3.  Logs the ingestion status to Firestore.

### 2. Nightly Evaluation Pipeline
*   **File**: `xyz/pipelines/evaluation_pipeline.py`
*   **Trigger**: Cloud Scheduler (e.g., nightly).
*   **Function**:
    1.  Fetches the last 24 hours of request logs from BigQuery.
    2.  Uses an **LLM-as-a-Judge** (Gemini) to score responses on Correctness, Relevance, and Completeness.
    3.  Writes scores to BigQuery (`llmops.evaluation_results`).
    4.  **Auto-Promotion**: If the average score meets a threshold, it can automatically promote a "candidate" prompt to "active" in Firestore.

### 3. Experiment Pipeline (A/B Testing)
*   **File**: `xyz/pipelines/experiment_pipeline.py`
*   **Trigger**: Manual or Weekly.
*   **Function**:
    1.  Loads a "Golden Dataset" (test questions) from GCS.
    2.  Runs Model A and Model B against these questions.
    3.  Uses an LLM Judge to compare answers side-by-side.
    4.  Declares a winner and optionally promotes the winning model in Firestore.

---

## Part 3: Setup & Prerequisites

### 1. Required GCP Services
Enable these APIs in your Google Cloud Project:
*   `aiplatform.googleapis.com` (Vertex AI)
*   `bigquery.googleapis.com`
*   `firestore.googleapis.com`
*   `storage.googleapis.com`
*   `cloudbuild.googleapis.com` (for building pipeline images, if needed)

### 2. IAM Permissions
The Service Account running these components needs:
*   **Vertex AI User**: To run pipelines and use Gemini.
*   **BigQuery Data Editor**: To read/write logs.
*   **Storage Object Viewer**: To read docs and pipeline artifacts.
*   **Firestore User**: To read/write configs.

### 3. Local Environment Variables
Update your `.env` file:
```bash
# Agent Config
BIGQUERY_PROJECT=your-project-id

# Pipeline Config
PIPELINE_LOCATION=us-central1
PIPELINE_ROOT_GCS=gs://your-project-pipeline-artifacts/
INVOKE_URL=https://your-api-url.com # For experiment pipeline
```

---

## Part 4: Commands & Usage

### 1. Running the Agent (Local)
Test the agent's ability to use tools:

```bash
# Start the server
uvicorn app.main:app --reload

# In another terminal, invoke the agent
# Ensure 'mock_app' is configured with "pipeline": "agent" in Firestore
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"app_id": "mock_app", "user_input": "Calculate 50 * 10 + 2"}'
```

### 2. Compiling & Submitting Pipelines

**RAG Ingestion:**
```bash
python xyz/pipelines/rag_ingestion_pipeline.py \
  --project YOUR_PROJECT_ID \
  --gcs_uri gs://your-bucket/doc.pdf \
  --submit
```

**Evaluation:**
```bash
python xyz/pipelines/evaluation_pipeline.py \
  --project YOUR_PROJECT_ID \
  --submit
```

**Experiment:**
```bash
python xyz/pipelines/experiment_pipeline.py \
  --project YOUR_PROJECT_ID \
  --model_a gemini \
  --model_b claude \
  --test_file gs://your-bucket/test_set.json \
  --submit
```

### 3. Setting up GCS Triggers
To auto-trigger ingestion when files are uploaded:
```bash
chmod +x xyz/scripts/setup_gcs_trigger.sh
./xyz/scripts/setup_gcs_trigger.sh YOUR_PROJECT_ID
```
