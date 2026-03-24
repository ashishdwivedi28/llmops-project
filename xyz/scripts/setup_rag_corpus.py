"""
Creates a Vertex AI RAG Engine corpus for each app that uses RAG.
Run once per app_id that has pipeline=rag.

us-west1
Usage: python scripts/setup_rag_corpus.py --project YOUR_PROJECT_ID --app_id rag_bot
"""
import argparse
import logging

import vertexai
from google.cloud import firestore
from vertexai.preview import rag

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_corpus(project_id: str, app_id: str, location: str = "us-central1") -> str:
    """Create a RAG Engine corpus and save its ID to Firestore."""
    vertexai.init(project=project_id, location=location)

    corpus_display_name = f"llmops_{app_id}_corpus"

    logger.info(f"Creating RAG corpus: {corpus_display_name}")

    # Embedding model config
    embedding_config = rag.EmbeddingModelConfig(
        publisher_model="publishers/google/models/text-embedding-004"
    )

    corpus = rag.create_corpus(
        display_name=corpus_display_name,
        embedding_model_config=embedding_config,
    )

    corpus_name = corpus.name
    logger.info(f"Corpus created: {corpus_name}")

    # Save corpus_id to Firestore so the serving pipeline can find it
    db = firestore.Client(project=project_id)
    db.collection("configs").document(app_id).update({
        "rag_corpus_id": corpus_name
    })
    logger.info(f"Corpus ID saved to Firestore for {app_id}")

    return corpus_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--app_id", required=True)
    parser.add_argument("--location", default="us-west1")
    args = parser.parse_args()

    corpus_id = create_corpus(args.project, args.app_id, args.location)
    print(f"\nCorpus ID: {corpus_id}")
    print(f"Add this to your .env file as RAG_LOCATION={args.location}")
