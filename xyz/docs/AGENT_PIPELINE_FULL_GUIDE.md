# Agentic Pipeline: Comprehensive Guide

This document provides a complete overview of the **Agentic Pipeline** within the LLMOps project. It explains what it is, how it works, its components, setup instructions, and how to run it.

---

## 1. What is the Agentic Pipeline?

The Agentic Pipeline (`AgentPipeline`) is an advanced AI workflow that goes beyond simple "prompt-response" interactions. Instead of just answering a user's question directly, it uses a **ReAct (Reasoning + Acting)** framework.

### Core Concept: ReAct
The agent follows a loop:
1.  **Think**: Analyze the user's request.
2.  **Act**: Decide which tool to use (e.g., query a database, search for files, calculate a value) to get missing information.
3.  **Observe**: Look at the output of that tool.
4.  **Repeat**: If more info is needed, loop back to "Think".
5.  **Final Answer**: Once enough info is gathered, provide the final response to the user.

This implementation leverages the **Google Agent Development Kit (ADK)** to manage this loop efficiently.

---

## 2. Components

### A. Core Code
*   **Location**: `xyz/app/pipelines/agent_pipeline.py`
*   **Class**: `AgentPipeline`
*   **Responsibility**: Initializes the ADK agent, defines the available tools, and manages the execution flow. It also includes a fallback mechanism to a standard LLM if the agent framework encounters issues.

### B. Tools
The agent has access to specific Python functions ("tools") that it can invoke:

1.  **`bigquery_query(sql_query)`**
    *   **Purpose**: Executes READ-ONLY SQL `SELECT` queries against your Google BigQuery dataset.
    *   **Use Case**: "How many users signed up last week?", "What is the average order value?"
    *   **Safety**: Strictly validates that queries start with `SELECT` to prevent data modification.

2.  **`list_gcs_files(bucket_name, prefix)`**
    *   **Purpose**: Lists files in a Google Cloud Storage (GCS) bucket.
    *   **Use Case**: "What documents are in the 'reports' folder?", "Do we have the Q3 financial PDF?"

3.  **`calculate(expression)`**
    *   **Purpose**: A safe mathematical calculator.
    *   **Use Case**: "Calculate 15% of 8,500", "What is 50 * 10 + 2?"
    *   **Why?**: LLMs often make arithmetic errors; this tool ensures 100% precision.

### C. LLM Provider
*   **Location**: `xyz/app/services/llm_provider.py`
*   **Role**: Handles the connection to Vertex AI (Gemini models).
*   **Models**: Supports models like `gemini-2.0-flash` and `gemini-2.5-flash`.

### D. Configuration (Firestore)
The pipeline is dynamic and controlled by configuration stored in Firestore (or passed at runtime).
*   **`pipeline`**: Must be set to `"agent"`.
*   **`model`**: The model to drive the agent (e.g., `"gemini-2.0-flash"`).
*   **`system_prompt`**: Instructions for the agent (e.g., "You are a data analyst...").

---

## 3. How to Setup

### Prerequisites
1.  **Google Cloud Project**: You need an active GCP project.
2.  **APIs Enabled**:
    *   Vertex AI API (`aiplatform.googleapis.com`)
    *   BigQuery API (`bigquery.googleapis.com`)
    *   Cloud Storage API (`storage.googleapis.com`)

### Environment Variables
Create or update your `.env` file in the `xyz/` directory:

```bash
# Required for Vertex AI and BigQuery
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
BIGQUERY_PROJECT=your-gcp-project-id
VERTEXAI_LOCATION=us-central1

# Optional: If using Anthropic models
ANTHROPIC_API_KEY=your-api-key
```

### IAM Permissions
The Service Account (or your user account if running locally) needs these roles:
*   **Vertex AI User**: To invoke Gemini models.
*   **BigQuery Data Viewer/Job User**: To run queries.
*   **Storage Object Viewer**: To list files in buckets.
*   **Firestore User**: To fetch app configurations.

---

## 4. How to Run It

### Option A: Local Testing via API (Recommended)

1.  **Start the Backend Server**:
    Navigate to the `xyz/` directory and run:
    ```bash
    cd xyz
    uvicorn app.main:app --reload --port 8000
    ```

2.  **Trigger the Agent**:
    Open a new terminal and send a POST request. Ensure you have an app ID configured in Firestore (or use a mock/test ID if your local setup supports it).

    **Example 1: Math Request**
    ```bash
    curl -X POST http://localhost:8000/invoke \
      -H "Content-Type: application/json" \
      -d '{
        "app_id": "test_agent_app",
        "user_input": "Calculate 125 * 45 and add 500."
      }'
    ```

    **Example 2: Data Request (BigQuery)**
    ```bash
    curl -X POST http://localhost:8000/invoke \
      -H "Content-Type: application/json" \
      -d '{
        "app_id": "test_agent_app",
        "user_input": "Query BigQuery to list the first 5 tables in the public dataset."
      }'
    ```

### Option B: Running Tests
You can run the unit tests to verify the agent logic without starting the full server.

```bash
cd xyz
pytest tests/unit/test_agent_pipeline.py
```

---

## 5. Troubleshooting

*   **"ADK not installed"**: The agent falls back to a simple LLM if the Google ADK library is missing. Ensure it is installed in your environment.
*   **"BigQuery not configured"**: Check that `BIGQUERY_PROJECT` is set in your `.env` file.
*   **"Query failed"**: The agent only allows `SELECT` statements. Ensure the model is generating valid SQL and that your user has permission to query the target dataset.
*   **Empty Response**: If the agent thinks but produces no final text, check the logs (`uvicorn` output) to see the internal "Think" steps.
