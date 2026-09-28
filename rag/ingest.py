import os
import time
import json
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from core.config import PINECONE_API_KEY, PINECONE_INDEX_NAME, OPENAI_API_KEY
from rag.custom_bm25 import CustomBM25Encoder

def init_pinecone_index():
    """Initializes the Pinecone serverless index if it does not exist, uses dotproduct for hybrid search."""
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Check if index exists and has the right dimension and metric
    if PINECONE_INDEX_NAME in pc.list_indexes().names():
        info = pc.describe_index(PINECONE_INDEX_NAME)
        if info.dimension != 1536 or info.metric != 'dotproduct':
            print(f"Deleting old Pinecone index {PINECONE_INDEX_NAME} (dimension or metric mismatch for hybrid search)")
            pc.delete_index(PINECONE_INDEX_NAME)
            time.sleep(5) # Give it a moment to clear
    
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating Pinecone index: {PINECONE_INDEX_NAME} (metric=dotproduct)")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=1536, # OpenAI text-embedding-3-small
            metric='dotproduct', # REQUIRED FOR HYBRID SEARCH
            spec=ServerlessSpec(cloud='aws', region='us-east-1')
        )
        # Wait for index to be initialized
        while not pc.describe_index(PINECONE_INDEX_NAME).status['ready']:
            time.sleep(1)
    
    return pc.Index(PINECONE_INDEX_NAME)

def purge_old_document_vectors(filename: str):
    """Removes outdated chunks by metadata filter."""
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)
    
    try:
        index.delete(filter={"source": filename})
        print(f"Successfully purged old vectors for {filename}")
    except Exception as e:
        print(f"Error purging old vectors: {str(e)}")

def ingest_pdf_file(pdf_path: str, original_filename: str = None):
    """Loads a PDF, splits it, assigns deterministic IDs, generates sparse/dense vectors, and upserts."""
    # Ensure index exists
    index = init_pinecone_index()
    
    filename = original_filename if original_filename else os.path.basename(pdf_path)
    
    print(f"Loading {filename}...")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    print(f"Splitting text...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(documents)
    
    corpus = []
    ids = []
    for idx, doc in enumerate(docs):
        # Override source metadata to ensure exact matching for purging later
        doc.metadata['source'] = filename
        doc.metadata['text'] = doc.page_content # INJECT TEXT FOR RETRIEVAL LATER
        ids.append(f"{filename}_chunk_{idx}")
        corpus.append(doc.page_content)
        
    print("Training BM25 Sparse Encoder...")
    bm25_path = "bm25_encoder.json"
    bm25 = CustomBM25Encoder()
    # In a production environment, you would merge vocabularies instead of resetting, 
    # but for this demo we'll just fit on the current doc + existing if we can.
    # We will just fit on the current doc for simplicity since the user typically uploads one by one.
    bm25.fit(corpus)
    bm25.dump(bm25_path)

    print(f"Generating dense and sparse vectors for {len(docs)} chunks...")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small", 
        openai_api_key=OPENAI_API_KEY
    )
    
    dense_vecs = embeddings.embed_documents(corpus)
    sparse_vecs = [bm25.encode_documents(text) for text in corpus]
    
    vectors_to_upsert = []
    for i in range(len(docs)):
        vectors_to_upsert.append({
            "id": ids[i],
            "values": dense_vecs[i],
            "sparse_values": sparse_vecs[i],
            "metadata": docs[i].metadata
        })
        
    print(f"Upserting {len(vectors_to_upsert)} hybrid chunks to Pinecone...")
    batch_size = 100
    for i in range(0, len(vectors_to_upsert), batch_size):
        index.upsert(vectors=vectors_to_upsert[i:i+batch_size])
        
    print(f"Finished ingesting {filename}.")
