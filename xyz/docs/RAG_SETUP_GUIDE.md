# RAG Pipeline Setup Guide

This document explains the recent upgrade to our Retrieval-Augmented Generation (RAG) pipeline, how it works, and the commands required to set it up and test it.

## What We Did (Run B)

We replaced the mock/placeholder RAG implementation with a **Real RAG Pipeline** powered by **Google Vertex AI RAG Engine**.

Previously, the `RAGPipeline` just returned a hardcoded string or a mock response. Now, it:
1.  **Connects to a Vertex AI Corpus**: A managed vector database in Google Cloud.
2.  **Retrieves Relevant Context**: Searches for documents relevant to the user's query.
3.  **Generates an Answer**: Sends the retrieved context + user query to the LLM (Gemini) to generate a grounded response.

---

## 1. Prerequisites & Setup

### Environment Variables
Ensure your `.env` file (or environment variables) includes:
```bash
GOOGLE_CLOUD_PROJECT=your_project_id
RAG_LOCATION=us-central1
# ... other existing variables
```
*Note: Vertex AI RAG Engine is currently best supported in `us-central1`.*

### Install Dependencies
We added `google-cloud-aiplatform` and `vertexai` to `requirements.txt`.
```bash
pip install -r requirements.txt
```

### Google Cloud Permissions
Your authenticated user (or service account) needs these roles:
*   `Vertex AI Administrator` or `Vertex AI User`
*   `Firestore User` (to save the config)

 Authenticate locally:
```bash
gcloud auth application-default login
```

---

## 2. Key Components & Code Explanation

### `xyz/scripts/setup_rag_corpus.py`
**Purpose**: Creates the "knowledge base" (Corpus) in Vertex AI.
*   It initializes a new RAG Corpus on Vertex AI.
*   It automatically updates your app's configuration in **Firestore** (`configs/{app_id}`) with the new `rag_corpus_id`.
*   **Run this once** per app that needs RAG.

### `xyz/app/pipelines/rag_pipeline.py`
**Purpose**: The runtime logic for answering questions.
*   **`_init_rag()`**: Lazy-loads the Vertex AI client (only when needed).
*   **`_retrieve_context()`**: Queries the Corpus using the `corpus_id` from the config. It gets the most relevant chunks of text.
*   **`execute()`**:
    1.  Gets context from `_retrieve_context()`.
    2.  Fills the prompt template: `Context: {context} 
 User: {user_input}`.
    3.  Calls the LLM (Gemini) to generate the final answer.
    4.  Returns the answer AND the number of chunks found (for logging).

### `xyz/app/routes.py`
**Purpose**: The API endpoint (`/invoke`).
*   Updated to handle the tuple return from RAG (`text, num_chunks`).
*   Logs the `retrieved_chunks` count to BigQuery so we can track data quality.

---

## 3. Step-by-Step Execution Guide

### Step 1: Create the RAG Corpus
Run the setup script for your RAG app (e.g., `rag_bot`):

```bash
# Replace YOUR_PROJECT_ID with your actual GCP project ID
python xyz/scripts/setup_rag_corpus.py --project YOUR_PROJECT_ID --app_id rag_bot
```

**Success Output**:
> Corpus created: projects/123.../locations/us-central1/ragCorpora/456...
> Corpus ID saved to Firestore for rag_bot

### Step 2: Add Documents (Manual for now)
Currently, we ingest documents manually via a script or CLI. (Automated ingestion is part of a future "Run D").

Run this Python snippet to upload a test file (e.g., a PDF or TXT):

```bash
python -c "
import vertexai
from vertexai.preview import rag
from google.cloud import firestore

# 1. Setup
project_id = 'YOUR_PROJECT_ID'  # <--- CHANGE THIS
app_id = 'rag_bot'
location = 'us-central1'

vertexai.init(project=project_id, location=location)

# 2. Get Corpus ID from Firestore
db = firestore.Client(project=project_id)
config = db.collection('configs').document(app_id).get().to_dict()
corpus_name = config.get('rag_corpus_id')

print(f'Uploading to: {corpus_name}')

# 3. Upload File (Change path to a real file on your disk)
# Create a dummy file if you don't have one
with open('test_knowledge.txt', 'w') as f:
    f.write('The secret code for the vault is 998877.')

rag.upload_file(
    corpus_name=corpus_name,
    path='test_knowledge.txt',
    display_name='Secret Codes',
)
print('Upload complete!')
"
```

### Step 3: Run the Application
Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

### Step 4: Test the Endpoint
Send a request that requires knowledge from the uploaded document:

```bash
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d 
  {
    "app_id": "rag_bot",
    "user_input": "What is the secret code for the vault?"
  }
```

**Expected Response**:
The `output` field should contain "998877" or whatever information was in your uploaded file.

---

## Troubleshooting

*   **"RAG not configured"**: Check if `rag_corpus_id` exists in Firestore for your `app_id`. Run Step 1 again if needed.
*   **"Permission Denied"**: Ensure you ran `gcloud auth application-default login`.
*   **Empty Response**: Ensure the file was actually uploaded (Step 2) and that the question is relevant to the file content.
