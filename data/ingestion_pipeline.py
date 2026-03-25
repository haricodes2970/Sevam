"""
Medical knowledge ingestion pipeline.
Orchestrates loading, cleaning, chunking, and saving medical documents.

Run: python data/ingestion_pipeline.py
"""

import json
import os
from cleaner import clean_document
from chunker import chunk_document


def load_knowledge_source(filepath: str) -> list:
    """
    Load raw medical documents from a JSON file.
    
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
    Save processed chunks to a JSON file.
    
    Args:
        chunks: List of processed chunk dictionaries
        output_path: Where to save the output file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"  Saved {len(chunks)} chunks to {output_path}")


def run_pipeline(input_path: str, output_path: str) -> list:
    """
    Run the full ingestion pipeline on a knowledge source file.
    
    Steps:
        1. Load raw documents
        2. Clean each document
        3. Chunk each document
        4. Validate output
        5. Save processed chunks
        
    Args:
        input_path: Path to raw JSON knowledge source
        output_path: Path to save processed chunks
        
    Returns:
        List of all processed chunks
    """
    print("\n--- Step 1: Loading documents ---")
    raw_docs = load_knowledge_source(input_path)

    print("\n--- Step 2: Cleaning documents ---")
    cleaned_docs = []
    for doc in raw_docs:
        cleaned = clean_document(doc)
        cleaned_docs.append(cleaned)
        print(f"  Cleaned: {cleaned['title']} ({cleaned['word_count']} words)")

    print("\n--- Step 3: Chunking documents ---")
    all_chunks = []
    for doc in cleaned_docs:
        chunks = chunk_document(doc, chunk_size=150, overlap=30)
        all_chunks.extend(chunks)
        print(f"  {doc['title']} → {len(chunks)} chunk(s)")

    print("\n--- Step 4: Validating ---")
    valid_chunks = [c for c in all_chunks if len(c['content'].split()) >= 20]
    removed = len(all_chunks) - len(valid_chunks)
    print(f"  Total chunks: {len(all_chunks)}")
    print(f"  Removed (too short): {removed}")
    print(f"  Valid chunks: {len(valid_chunks)}")

    print("\n--- Step 5: Saving ---")
    save_processed_chunks(valid_chunks, output_path)

    return valid_chunks


def print_sample(chunks: list, n: int = 2) -> None:
    """Print a sample of chunks to verify output looks correct."""
    print(f"\n--- Sample output (first {n} chunks) ---")
    for chunk in chunks[:n]:
        print(f"\n  chunk_id : {chunk['chunk_id']}")
        print(f"  title    : {chunk['title']}")
        print(f"  source   : {chunk['source']}")
        print(f"  words    : {chunk['word_count']}")
        print(f"  emergency: {chunk['is_emergency']}")
        print(f"  content  : {chunk['content'][:120]}...")


if __name__ == "__main__":
    print("🩺 Sevam — Knowledge Ingestion Pipeline\n")

    input_path  = "data/knowledge_sources/medical_knowledge.json"
    output_path = "data/processed/processed_chunks.json"

    chunks = run_pipeline(input_path, output_path)
    print_sample(chunks)

    print("\n✅ Pipeline complete! Ready for Phase 3 (RAG embeddings).\n")
