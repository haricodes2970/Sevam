"""
Ayurvedic knowledge ingestion pipeline for Sevam.
Orchestrates: Load -> Clean -> Chunk -> Embed -> Store in ChromaDB.

Run: python data/ingestion_pipeline.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data.cleaner import clean_text
from data.chunker import chunk_document
from ai.embeddings.embedder import MedicalEmbedder
from backend.rag_pipeline.vector_store import MedicalVectorStore


KNOWLEDGE_PATH = "data/knowledge_sources/ayurveda_knowledge.json"
PROCESSED_PATH = "data/processed/processed_chunks.json"


def load_knowledge_source(filepath: str) -> list:
    """
    Load raw Ayurvedic knowledge documents from a JSON file.

    Args:
        filepath: Path to the JSON knowledge source file

    Returns:
        List of raw document dictionaries
    """
    print(f"  Loading: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    print(f"  Loaded {len(documents)} documents")
    return documents


def save_processed_chunks(chunks: list, output_path: str) -> None:
    """
    Save processed chunks to a JSON file for inspection.

    Args:
        chunks: List of processed chunk dictionaries
        output_path: Where to save the output file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Remove embeddings before saving (too large for JSON inspection)
    saveable = [{k: v for k, v in c.items() if k != "embedding"} for c in chunks]
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(saveable, f, indent=2, ensure_ascii=False)
    print(f"  Saved {len(saveable)} chunks to {output_path}")


def run_pipeline(
    input_path: str = KNOWLEDGE_PATH,
    output_path: str = PROCESSED_PATH,
) -> list:
    """
    Run the full ingestion pipeline: Load -> Clean -> Chunk -> Embed -> Store.

    Args:
        input_path: Path to raw JSON knowledge source
        output_path: Path to save processed chunks (without embeddings)

    Returns:
        List of all processed chunks with embeddings
    """
    print("\n--- Step 1: Loading documents ---")
    raw_docs = load_knowledge_source(input_path)

    print("\n--- Step 2: Cleaning documents ---")
    for doc in raw_docs:
        doc["content"] = clean_text(doc["content"])
        word_count = len(doc["content"].split())
        print(f"  Cleaned: {doc['title']} ({word_count} words)")

    print("\n--- Step 3: Chunking documents ---")
    all_chunks = []
    for doc in raw_docs:
        chunks = chunk_document(doc, chunk_size=150, overlap=30)
        all_chunks.extend(chunks)
        print(f"  {doc['title']} -> {len(chunks)} chunk(s)")

    print(f"\n  Total chunks: {len(all_chunks)}")

    # Filter out very short chunks
    valid_chunks = [c for c in all_chunks if len(c["content"].split()) >= 20]
    removed = len(all_chunks) - len(valid_chunks)
    if removed:
        print(f"  Removed {removed} chunks (too short)")
    print(f"  Valid chunks: {len(valid_chunks)}")

    print("\n--- Step 4: Generating embeddings ---")
    embedder = MedicalEmbedder()
    texts = [c["content"] for c in valid_chunks]
    embeddings = embedder.embed_batch(texts)
    for chunk, emb in zip(valid_chunks, embeddings):
        chunk["embedding"] = emb

    print("\n--- Step 5: Storing in ChromaDB ---")
    vector_store = MedicalVectorStore()
    if vector_store.count() > 0:
        print(f"  Clearing {vector_store.count()} existing docs for fresh index")
        vector_store.clear()
    vector_store.add_documents(valid_chunks)

    print("\n--- Step 6: Saving processed chunks ---")
    save_processed_chunks(valid_chunks, output_path)

    print(f"\n  Pipeline complete! {vector_store.count()} chunks indexed.")
    return valid_chunks


if __name__ == "__main__":
    print("Sevam -- Ayurvedic Knowledge Ingestion Pipeline\n")
    run_pipeline()
