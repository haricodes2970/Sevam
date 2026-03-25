"""
RAG indexing pipeline.
Loads processed chunks, generates embeddings, stores in ChromaDB.

Run once to build the vector index:
    python backend/rag_pipeline/indexer.py
"""

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.embeddings.embedder import MedicalEmbedder
from backend.rag_pipeline.vector_store import MedicalVectorStore


CHUNKS_PATH = "data/processed/processed_chunks.json"


def load_chunks(filepath: str) -> list:
    """
    Load processed chunks from JSON file.

    Args:
        filepath: Path to processed_chunks.json

    Returns:
        List of chunk dictionaries
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    print(f"  Loaded {len(chunks)} chunks from {filepath}")
    return chunks


def run_indexing(chunks_path: str = CHUNKS_PATH) -> None:
    """
    Full indexing pipeline:
    1. Load chunks
    2. Generate embeddings
    3. Store in ChromaDB

    Args:
        chunks_path: Path to the processed chunks JSON file
    """
    print("\n--- Step 1: Loading chunks ---")
    chunks = load_chunks(chunks_path)

    print("\n--- Step 2: Initializing models ---")
    embedder = MedicalEmbedder()
    vector_store = MedicalVectorStore()

    # Clear old data to avoid duplicates on re-run
    if vector_store.count() > 0:
        print(f"  Found {vector_store.count()} existing docs — clearing for fresh index")
        vector_store.clear()

    print("\n--- Step 3: Generating embeddings ---")
    texts = [chunk["content"] for chunk in chunks]
    embeddings = embedder.embed_batch(texts)

    print("\n--- Step 4: Storing in ChromaDB ---")
    chunk_ids  = [chunk["chunk_id"] for chunk in chunks]
    documents  = [chunk["content"] for chunk in chunks]
    metadatas  = [
        {
            "title":        chunk.get("title", ""),
            "source":       chunk.get("source", ""),
            "chunk_index":  str(chunk.get("chunk_index", 0)),
            "parent_id":    chunk.get("parent_id", ""),
            "is_emergency": str(chunk.get("is_emergency", False)),
            "word_count":   str(chunk.get("word_count", 0)),
        }
        for chunk in chunks
    ]

    vector_store.add_documents(chunk_ids, embeddings, documents, metadatas)

    print(f"\n✅ Indexing complete! {vector_store.count()} chunks indexed in ChromaDB.")


if __name__ == "__main__":
    print("🔍 Sevam — RAG Indexing Pipeline\n")
    run_indexing()
