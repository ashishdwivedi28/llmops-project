# Kubeflow Pipelines (KFP) & Automation Guide

This document provides a detailed technical overview of the automation pipelines in the `xyz/` directory. It analyzes their architecture, explains how to use them, and recommends best practices for production deployment.

---

## 1. Architecture Overview

The system uses **Vertex AI Pipelines** (based on Kubeflow) to handle asynchronous, compute-intensive tasks. Unlike the real-time API (FastAPI), these pipelines run in the background, triggered by events or schedules.

### The "Master Pipeline" Strategy
While there are standalone pipeline files (`rag_ingestion_pipeline.py`, etc.), the **`master_pipeline.py`** is the recommended production entry point.

**Why?**
1.  **Unified Deployment**: You only need to deploy one pipeline definition to Vertex AI.
2.  **Artifact Handling**: The master pipeline uses KFP **Artifacts** (GCS blobs) to pass data between steps. The standalone scripts often pass JSON strings, which breaks if data exceeds 2MB (KFP limit).
3.  **Conditional Logic**: It uses a `trigger_type` parameter to decide which workflow to run.

---

## 2. The Master Pipeline (`pipelines/master_pipeline.py`)

This pipeline acts as a central controller. It takes a `trigger_type` argument to switch between three distinct modes.

### Modes (Branches)

| `trigger_type` | Description | Triggered By |
| :--- | :--- | :--- |
| **`rag_ingestion`** | Ingests a file from GCS into the RAG Corpus. | File Upload (via Eventarc) |
| **`evaluation`** | Fetches logs, runs "LLM-as-Judge", and updates config. | Nightly Schedule (Cloud Scheduler) |
| **`experiment`** | Runs A/B tests on models and promotes the winner. | Weekly Schedule or Manual |
| **`full_run`** | Runs Evaluation followed by an Experiment. | Manual System Check |

### Usage

**1. Compilation**
First, compile the Python code into a JSON pipeline specification.
```bash
python xyz/pipelines/master_pipeline.py --project YOUR_PROJECT_ID --compile
# Output: master_pipeline.json
```

**2. Submission (Manual)**
You can submit a run from the CLI:
```bash
python xyz/pipelines/master_pipeline.py \
  --project YOUR_PROJECT_ID \
  --submit \
  --trigger_type evaluation \
  --app_id my_chat_app
```

---

## 3. Pipeline Workflows in Detail

### A. RAG Ingestion Branch
*   **Goal**: Keep the knowledge base up-to-date automatically.
*   **Steps**:
    1.  **`ingest_document_to_rag`**:
        *   Reads `rag_corpus_id` from Firestore (`configs/{app_id}`).
        *   Uses `vertexai.preview.rag.upload_file` to index the document.
        *   Logs the success/failure to Firestore (`ingestion_log`).

### B. Nightly Evaluation Branch
*   **Goal**: Monitor quality and auto-improve prompts.
*   **Steps**:
    1.  **`fetch_logs_to_gcs`**:
        *   Queries BigQuery for the last `lookback_hours` of request logs.
        *   Writes the result to a GCS Artifact (handling large datasets safely).
    2.  **`score_responses_with_judge`**:
        *   Reads logs from the artifact.
        *   Uses a "Judge" model (e.g., `gemini-2.0-pro`) to score each response (1-5) on **Correctness**, **Relevance**, and **Completeness**.
    3.  **`update_active_config`**:
        *   Calculates the average score.
        *   **Auto-Promotion Logic**: If the average score drops below `evaluation_threshold`, it checks Firestore for "candidate" prompts. If a candidate has a higher pre-calculated score, it automatically swaps the `active_prompt_version`.

### C. Experiment Branch (A/B Testing)
*   **Goal**: Scientifically compare two models (e.g., Gemini 2.0 Flash vs Pro).
*   **Steps**:
    1.  **`load_test_set_from_gcs`**: Loads a "Golden Dataset" of QA pairs.
    2.  **`run_model_inference` (Parallel)**:
        *   Runs Model A and Model B in parallel against the test set.
    3.  **`compare_models_and_promote`**:
        *   The Judge model compares the answers side-by-side.
        *   Declares a winner.
        *   **Auto-Promotion**: If the winner wins by a configured `promotion_margin` (e.g., >0.5 points), it updates Firestore to set `active_model` to the winner.

---

## 4. Code Analysis & Cloud Readiness

### Correctness Check
*   **KFP DSL**: The code correctly uses `@dsl.component` and `@dsl.pipeline`.
*   **Data Passing**: The `master_pipeline.py` correctly uses `dsl.Input[dsl.Artifact]` and `dsl.Output[dsl.Artifact]`. This is **critical** for cloud stability. The standalone scripts (`evaluation_pipeline.py`) pass raw strings, which poses a risk of `Print message is too long` errors in production.
*   **Dependencies**: The base images (`python:3.11-slim`) and packages (`google-cloud-aiplatform`, `vertexai`) are correct.

### Recommendation
**ALWAYS use `master_pipeline.py`.**
Do not deploy the standalone `evaluation_pipeline.py` or `experiment_pipeline.py` for production workloads unless you are certain your data is tiny (<2MB). The master pipeline is the robust, scalable implementation.

### Configuration Note
The pipelines rely on `google_api_key` for some components (specifically `google.generativeai`).
*   **Best Practice**: Ensure you pass the `GOOGLE_API_KEY` as a pipeline parameter or, preferably, refactor to use `vertexai` (which uses the Service Account) for all calls. The current code mixes both.

---

## 5. Setup Instructions

1.  **Service Account**: Ensure the Compute Engine default service account (or your custom pipeline SA) has:
    *   `Vertex AI User`
    *   `BigQuery Data Editor`
    *   `Storage Object Admin`
    *   `Datastore User` (for Firestore)

2.  **Bucket**: Create a bucket for artifacts.
    ```bash
    export PIPELINE_ROOT_GCS="gs://your-project-artifacts"
    ```

3.  **Deploy**:
    Run the master pipeline script with `--submit` to launch jobs on Vertex AI.
