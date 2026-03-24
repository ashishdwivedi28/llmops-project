import logging
import vertexai
from vertexai.preview import rag
from google.cloud import firestore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = "project-3e17312f-26d8-4511-821"
LOCATION = "us-west1" # RAG is usually in us-west1 or us-central1 depending on setup. The previous output showed us-west1.

def check_status():
    print(f"--- 🔍 Checking RAG Status for {PROJECT_ID} ---")
    
    # 1. Identify Active Corpus from Firestore
    db = firestore.Client(project=PROJECT_ID)
    doc_ref = db.collection('configs').document('rag_bot')
    doc = doc_ref.get()
    
    active_corpus_id = None
    if doc.exists:
        config = doc.to_dict()
        active_corpus_id = config.get('rag_corpus_id')
        print(f"✅ Active App Config found. Linked Corpus ID: {active_corpus_id}")
    else:
        print(f"❌ No 'rag_bot' config found in Firestore.")

    # 2. List All Corpora
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    try:
        corpora = rag.list_corpora()
        print(f"\n--- 📚 Checking RAG Corpora ---")
        count = 0
        for c in corpora:
            count += 1
            is_active = " (⭐ ACTIVE)" if active_corpus_id and str(c.name) == str(active_corpus_id) else ""
            print(f"- Name: {c.display_name}")
            print(f"  ID: {c.name}{is_active}")
            
            # Try to list files for this corpus
            try:
                files = rag.list_files(corpus_name=c.name)
                # handle pager object
                file_list = list(files)
                print(f"  📄 Files: {len(file_list)}")
                for f in file_list:
                    print(f"    - {f.display_name}")
            except Exception as e:
                print(f"  ⚠️ Could not list files: {e}")
            print("")
        print(f"Total Corpora Found: {count}")
            
    except Exception as e:
        print(f"❌ Failed to list corpora: {e}")

if __name__ == "__main__":
    check_status()
