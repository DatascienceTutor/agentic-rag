import os
import glob
from ingest import ingest_pdf_file, init_pinecone_index
from pinecone import Pinecone
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME

def run_migration():
    print("Forcing recreation of Pinecone index for hybrid search...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    if PINECONE_INDEX_NAME in pc.list_indexes().names():
        pc.delete_index(PINECONE_INDEX_NAME)
        import time
        time.sleep(5)
    
    init_pinecone_index()
    
    data_dir = "data"
    if not os.path.exists(data_dir):
        print("Data directory not found. Please run the app and upload documents.")
        return
        
    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    if not pdf_files:
        print("No PDF files found in data directory.")
        return
        
    for pdf_file in pdf_files:
        print(f"Migrating {pdf_file}...")
        ingest_pdf_file(pdf_file)
        
    print("Migration complete! Hybrid search is now fully active.")

if __name__ == "__main__":
    run_migration()
