
# BigQuery Tables & Firestore Configuration Setup

## Overview
This document guides you through creating the necessary **BigQuery tables** for logging and the **Firestore database** for dynamic configuration. This setup is the foundation for Phase 2 of the LLMOps architecture.

## 1. BigQuery Tables Created
The setup script (`scripts/setup_bigquery.py`) creates a dataset named `llmops` and the following tables:

| Table Name | Description | Partitioning |
| :--- | :--- | :--- |
| **`requests`** | **(MAIN LOGS)** Logs every API request, including user input, model output, latency, and token counts. | Day |
| `evaluation_results` | Stores results from offline or online evaluations (e.g., correctness scores). | None |
| `experiments` | Tracks A/B testing results between different models or prompts. | None |

## 2. Firestore Configuration
The seeding script (`scripts/seed_firestore_config.py`) initializes the following collections in Firestore:

*   **`configs`**: Stores app-level settings (e.g., active model, temperature).
    *   **`prompts`** (Sub-collection): Stores versioned system prompts and templates.

---

## Setup Instructions

**Prerequisites:**
*   You must have a Google Cloud Project.
*   You must have `gcloud` installed and authenticated.
*   **Important:** Ensure your Firestore database is created in Native Mode before running the scripts.
    *   *Create here:* [https://console.cloud.google.com/datastore/setup](https://console.cloud.google.com/datastore/setup)

### Step 1: Install Dependencies
Navigate to the `xyz` directory and install the required Python packages:
```bash
cd xyz
pip install -r requirements.txt
```

### Step 2: Create BigQuery Tables
Run the setup script. Replace `YOUR_PROJECT_ID` with your actual project ID.
```bash
python scripts/setup_bigquery.py --project YOUR_PROJECT_ID
```
*   **Success Message:** `BigQuery setup complete.`

### Step 3: Seed Firestore Configuration
Run the seeding script to populate the initial config.
```bash
python scripts/seed_firestore_config.py --project YOUR_PROJECT_ID
```
*   **Success Message:** `Firestore seeding complete.`

---

## Where to View Logs

Once the application is running and requests are made, logs are streamed to BigQuery.

**Location:**
*   **Project:** `YOUR_PROJECT_ID`
*   **Dataset:** `llmops`
*   **Table:** `requests`

**How to Query Logs:**
You can view the logs in the [BigQuery Console](https://console.cloud.google.com/bigquery) by running this SQL query:

```sql
SELECT 
  timestamp,
  app_id,
  user_input,
  output,
  latency_ms,
  model
FROM 
  `YOUR_PROJECT_ID.llmops.requests`
ORDER BY 
  timestamp DESC 
LIMIT 100;
```

---

## Local Development Verification

To run the app locally using these cloud resources:

1.  **Export Environment Variables:**
    ```bash
    export FIRESTORE_PROJECT=YOUR_PROJECT_ID
    export BIGQUERY_PROJECT=YOUR_PROJECT_ID
    ```

2.  **Start the Server:**
    ```bash
    uvicorn app.main:app --reload
    ```

3.  **Send a Test Request:**
    ```bash
    curl -X POST http://localhost:8000/invoke \
         -H "Content-Type: application/json" \
         -d '{"app_id":"default_llm","user_input":"Testing BigQuery logging."}'
    ```

4.  **Check BigQuery:** Run the SQL query above to confirm the new row appears.
