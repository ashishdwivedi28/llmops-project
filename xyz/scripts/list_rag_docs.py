import argparse
import logging
import os
import vertexai
from vertexai.preview import rag
from google.cloud import firestore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def list_rag_documents(project_id: str, app_id: str, location: str = "us-west1"):
    """Lists documents in the Vertex AI RAG Corpus linked to the app."""
    
    # 1. Initialize Vertex AI
    vertexai.init(project=project_id, location=location)
    
    # 2. Get Corpus ID from Firestore
    db = firestore.Client(project=project_id)
    doc_ref = db.collection('configs').document(app_id)
    doc = doc_ref.get()
    
    if not doc.exists:
        logger.error(f"App config for '{app_id}' not found in Firestore.")
        return

    config = doc.to_dict()
    corpus_name = config.get('rag_corpus_id')
    
    if not corpus_name:
        logger.error(f"No 'rag_corpus_id' found for app '{app_id}'. Run setup_rag_corpus.py first.")
        return

    logger.info(f"Checking Corpus: {corpus_name}")
    
    try:
        # Use the corpus name directly to list files
        files = rag.list_files(corpus_name=corpus_name)
        if not files:
            print(f"No files found in corpus {corpus_name}.")
        else:
            print(f"\n--- Documents in RAG Corpus ({len(files)}) ---")
            for f in files:
                print(f"- {f.display_name} (ID: {f.name})")
            print("-----------------------------------")

    except Exception as e:
        logger.error(f"Failed to list files: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List documents in Vertex AI RAG Corpus")
    parser.add_argument("--project", required=True, help="GCP Project ID")
    parser.add_argument("--app_id", default="rag_bot", help="App ID in Firestore (default: rag_bot)")
    parser.add_argument("--location", default="us-west1", help="GCP Region (must match corpus location)")
    
    args = parser.parse_args()
    
    list_rag_documents(args.project, args.app_id, location=args.location)
