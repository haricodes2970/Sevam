"""
RAG indexing pipeline for Sevam.
Loads Ayurvedic knowledge, cleans, chunks, generates embeddings, stores in ChromaDB.

Run once to build the vector index:
    python backend/rag_pipeline/indexer.py
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.embeddings.embedder import MedicalEmbedder
from backend.rag_pipeline.vector_store import MedicalVectorStore
from data.cleaner import clean_text
from data.chunker import chunk_document


KNOWLEDGE_PATH = "data/knowledge_sources/ayurveda_knowledge.json"


def load_knowledge(filepath: str) -> list:
    """
    Load Ayurvedic knowledge documents from JSON file.

    Args:
        filepath: Path to ayurveda_knowledge.json

    Returns:
        List of document dictionaries
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        docs = json.load(f)
    print(f"  Loaded {len(docs)} documents from {filepath}")
    return docs


def run_indexing(knowledge_path: str = KNOWLEDGE_PATH) -> None:
    """
    Full indexing pipeline:
    1. Load Ayurvedic knowledge documents
    2. Clean and chunk each document
    3. Generate embeddings
    4. Store in ChromaDB

    Args:
        knowledge_path: Path to the Ayurvedic knowledge JSON file
    """
    print("\n--- Step 1: Loading Ayurvedic knowledge ---")
    docs = load_knowledge(knowledge_path)

    print("\n--- Step 2: Cleaning and chunking ---")
    all_chunks = []
    for doc in docs:
        doc["content"] = clean_text(doc["content"])
        chunks = chunk_document(doc, chunk_size=150, overlap=30)
        all_chunks.extend(chunks)
        print(f"  [{doc['id']}] {doc['title']} -> {len(chunks)} chunk(s)")

    print(f"\n  Total chunks: {len(all_chunks)}")

    print("\n--- Step 3: Initializing models ---")
    embedder = MedicalEmbedder()
    vector_store = MedicalVectorStore()

    if vector_store.count() > 0:
        print(f"  Found {vector_store.count()} existing docs — clearing for fresh index")
        vector_store.clear()

    print("\n--- Step 4: Generating embeddings ---")
    texts = [chunk["content"] for chunk in all_chunks]
    embeddings = embedder.embed_batch(texts)

    # Attach embeddings to chunks
    for chunk, emb in zip(all_chunks, embeddings):
        chunk["embedding"] = emb

    print("\n--- Step 5: Storing in ChromaDB ---")
    vector_store.add_documents(all_chunks)

    print(f"\n  Indexing complete! {vector_store.count()} chunks indexed in ChromaDB.")


if __name__ == "__main__":
    print("Sevam — Ayurvedic Knowledge Indexer\n")
    run_indexing()
