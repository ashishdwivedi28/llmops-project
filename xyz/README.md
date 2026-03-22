# LLMOps Pipeline - Foundational Module

This repository contains the **Application Layer** and **Config System** for a modular, production-grade LLMOps pipeline built with **FastAPI**.

## 🚀 Overview

The system is designed to be:
1.  **Config-Driven**: Behavior (model, pipeline type) is controlled via `config/config.json`.
2.  **Modular**: The application logic is separated from configuration and utility functions.
3.  **Extensible**: Easily add new pipelines (e.g., agents, RAG) by updating the config.

### Core Components

*   **`app/`**: Contains the FastAPI application and route definitions.
*   **`app/services/`**: Model Abstraction Layer (Gemini, Claude, Mock), Task Detector, and Logging Service (BigQuery).
*   **`app/pipelines/`**: Execution Layer (LLMPipeline, RAG, Agent).
*   **`app/orchestrator/`**: Deterministic routing logic to select the correct pipeline.
*   **`app/tools/`**: Agent Tool definitions (Module 7).
*   **`config/`**: Stores the JSON configuration for different applications (`app_id`).
*   **`scripts/`**: Offline Evaluation scripts (Module 9).
*   **`pipelines/kfp/`**: Vertex AI (Kubeflow) Pipeline definitions (Module 10).
*   **`utils/`**: Reusable utility modules, such as the configuration loader.

---

## 🛠️ Configuration System

The behavior of the pipeline is defined in `config/config.json`. Each key represents a unique `app_id`.

**Example `config.json`:**
```json
{
  "rag_bot": {
    "pipeline": "rag",
    "model": "gemini",
    "prompt_template": "Context: [NONE]\nQuestion: {user_input}\nAnswer like a research assistant:"
  },
  "code_agent": {
    "pipeline": "agent",
    "model": "claude",
    "system_prompt": "You are a senior engineer... Available Tools:\n{tool_descriptions}",
    "max_iterations": 3
  }
}
```

### How it works:
1.  The API receives a request with an `app_id`.
2.  `utils.config_loader` reads `config.json`.
3.  **Task Detector** (Module 4) classifies the intent.
4.  **Orchestrator** (Module 5) uses the classification and config to pick the correct pipeline.
5.  **Agent Pipeline** (Module 7) uses a **ReAct loop** to reason and execute tools if necessary.
6.  **Logging Service** (Module 8) captures the request/response and latency, storing them in **BigQuery**.
7.  **Evaluation Script** (Module 9) pulls logs from BigQuery and uses an LLM to judge their quality.
8.  **Vertex Pipeline** (Module 10) automates this evaluation logic in the cloud.

---

## 📡 API Usage

### Endpoint: `POST /invoke`

**Request Body:**
```json
{
  "app_id": "code_agent",
  "user_input": "Calculate 2 + 2 and save the result as math_result.txt"
}
```

**Response (Success):**
```json
{
  "app_id": "code_agent",
  "user_input": "Calculate 2 + 2 and save the result as math_result.txt",
  "config": { "pipeline": "agent", "model": "claude", ... },
  "task_detection": { "needs_rag": false, "needs_agent": true },
  "pipeline_executed": "AgentPipeline",
  "output": "The result of 2 + 2 is 4, and it has been saved as 'math_result.txt' to GCS.",
  "latency_ms": 1250.45
}
```

---

## ⚖️ Evaluation (Module 9)

Run the offline evaluation script to grade the performance of your apps:

```bash
# Set Project ID
export GOOGLE_CLOUD_PROJECT=your-project-id

# Run the judge script
python scripts/evaluate.py
```

This will pull the latest 10 logs from BigQuery and use a high-capability LLM to score them for **Accuracy**, **Helpfulness**, and **Safety**.

---

## 🔄 Automated Lifecycle (Module 10)

To automate the evaluation process using Vertex AI Pipelines:

1.  **Compile the Pipeline:**
    ```bash
    python pipelines/kfp/vertex_pipeline.py
    ```
    This generates `llmops_pipeline.json`.

2.  **Upload to Vertex AI:**
    *   Go to Google Cloud Console -> **Vertex AI** -> **Pipelines**.
    *   Click **Create Run**.
    *   Upload `llmops_pipeline.json`.
    *   Ensure the service account has `BigQuery Data Viewer` and `Vertex AI User` roles.

---

## 💻 Local Development

### Prerequisites
*   Python 3.9+
*   `pip`
*   Google Cloud Project (with Vertex AI enabled) - *Optional for local mock testing*
*   `gcloud` CLI (authenticated via `gcloud auth application-default login`) - *Optional for local mock testing*

### 1. Setup & Install Dependencies

It is recommended to use a virtual environment.

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application
```bash
uvicorn app.main:app --reload --port 8000
```
The API will be available at `http://localhost:8000`.

### 3. Verify Functionality

#### A. Local Testing (No GCP Credentials)
You can test the pipeline flow locally without any Google Cloud credentials by using the `mock_app` configuration. This uses a mock LLM provider that echoes your input.

**Run the Mock Request:**
```bash
curl -X POST http://127.0.0.1:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "mock_app",
    "user_input": "Hello World"
  }'
```

**Expected Response:**
```json
{
  "app_id": "mock_app",
  "pipeline_executed": "LLMPipeline",
  "output": "[MOCK RESPONSE] Processed: 'Echo: Hello World'..."
}
```

#### B. Full Pipeline Testing (Requires GCP)
If you have `GOOGLE_CLOUD_PROJECT` set and `gcloud` authenticated, you can test the real pipelines:

```bash
curl -X POST http://127.0.0.1:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "app_id": "default_llm",
    "user_input": "Explain quantum computing in one sentence."
  }'
```

---

## ☁️ Google Cloud Deployment (Cloud Run)

### 1. Build and Deploy
Ensure you have the Google Cloud SDK installed and authenticated.

```bash
# Set your project ID
export PROJECT_ID=your-gcp-project-id

# Build the container image using Cloud Build
gcloud builds submit --tag gcr.io/$PROJECT_ID/llmops-pipeline

# Deploy to Cloud Run
gcloud run deploy llmops-service \
  --image gcr.io/$PROJECT_ID/llmops-pipeline \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 2. BigQuery Setup (Logging)
To enable logging, create a BigQuery dataset and table:
```bash
# Create Dataset
bq mk llmops_logs

# Create Table
bq mk --table YOUR_PROJECT_ID:llmops_logs.request_logs \
  timestamp:TIMESTAMP,app_id:STRING,user_input:STRING,output:STRING,model_name:STRING,pipeline_type:STRING,latency_ms:FLOAT,config_used:JSON,task_detection:JSON,metadata:JSON
```

---

## ⚠️ FAILURE & DEBUGGING

*   **Failure:** `ModuleNotFoundError: No module named 'app'`.
    *   **Fix:** Ensure you are running the script from the project root. Use `export PYTHONPATH=$PYTHONPATH:.` if necessary.
*   **Failure:** `❌ BigQuery Logger Failure: 404 Dataset not found.`
    *   **Fix:** Ensure you have created the BigQuery dataset and table as described above.
*   **Failure:** No logs in BigQuery during local test.
    *   **Fix:** Ensure `GOOGLE_CLOUD_PROJECT` environment variable is set and you have run `gcloud auth application-default login`.
