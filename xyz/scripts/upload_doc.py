import argparse
import logging
import os
import vertexai
from vertexai.preview import rag
from google.cloud import firestore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_document(project_id: str, app_id: str, file_path: str, location: str = "us-central1"):
    """Uploads a document to the Vertex AI RAG Corpus linked to the app."""
    
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

    logger.info(f"Uploading '{file_path}' to Corpus: {corpus_name}")

    # 3. Upload File
    try:
        rag.upload_file(
            corpus_name=corpus_name,
            path=file_path,
            display_name=os.path.basename(file_path),
        )
        logger.info(f"✅ Successfully uploaded {file_path}")
    except Exception as e:
        logger.error(f"❌ Failed to upload file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload a document to Vertex AI RAG Corpus")
    parser.add_argument("--project", required=True, help="GCP Project ID")
    parser.add_argument("--app_id", default="rag_bot", help="App ID in Firestore (default: rag_bot)")
    parser.add_argument("file_path", help="Path to the file to upload (PDF, TXT, etc.)")
    parser.add_argument("--location", default="us-central1", help="GCP Region")
    
    args = parser.parse_args()
    
    upload_document(args.project, args.app_id, args.file_path, args.location)
