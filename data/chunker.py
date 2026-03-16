"""
Document chunking module.
Splits medical documents into smaller overlapping chunks for RAG indexing.
"""

from typing import List


def chunk_text(text: str, chunk_size: int = 200, overlap: int = 40) -> List[str]:
    """
    Split text into overlapping chunks by word count.
    
    Why overlap? So that if an important sentence falls at the boundary
    of a chunk, it still appears in the next chunk too. This prevents
    losing context at chunk edges.
    
    Args:
        text: The text to split
        chunk_size: Number of words per chunk
        overlap: Number of words to repeat between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []

    words = text.split()

    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)

        # Move forward by chunk_size minus overlap
        start += chunk_size - overlap

        # Avoid infinite loop on very small texts
        if start >= len(words):
            break

    return chunks


def chunk_document(doc: dict, chunk_size: int = 200, overlap: int = 40) -> List[dict]:
    """
    Split a medical document into multiple chunk documents.
    
    Each chunk keeps the original metadata plus a chunk index,
    so we always know which document a chunk came from.
    
    Args:
        doc: Cleaned document dictionary
        chunk_size: Words per chunk
        overlap: Overlap words between chunks
        
    Returns:
        List of chunk dictionaries ready for embedding
    """
    content = doc.get('content', '')
    chunks = chunk_text(content, chunk_size, overlap)

    chunk_docs = []

    for i, chunk in enumerate(chunks):
        chunk_doc = {
            'chunk_id': f"{doc['id']}_chunk_{i}",
            'parent_id': doc['id'],
            'title': doc.get('title', ''),
            'source': doc.get('source', ''),
            'chunk_index': i,
            'total_chunks': len(chunks),
            'content': chunk,
            'word_count': len(chunk.split()),
            'is_emergency': doc.get('is_emergency', False),
        }
        chunk_docs.append(chunk_doc)

    return chunk_docs