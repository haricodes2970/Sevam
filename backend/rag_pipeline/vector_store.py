"""
Vector store module using ChromaDB for Sevam.
Stores and retrieves Ayurvedic knowledge document embeddings.
Collection: sevam_knowledge
"""

import chromadb
import os
from typing import List, Dict, Optional


CHROMA_DB_PATH = "./data/vector_db"
COLLECTION_NAME = "sevam_knowledge"


class MedicalVectorStore:
    """
    Manages the ChromaDB vector database for Ayurvedic knowledge.
    Handles storing, querying, and managing document embeddings.
    """

    def __init__(self, db_path: str = CHROMA_DB_PATH):
        """
        Initialize ChromaDB client and get or create collection.

        Args:
            db_path: Directory path where ChromaDB stores data
        """
        os.makedirs(db_path, exist_ok=True)

        print(f"  Connecting to ChromaDB at: {db_path}")
        self.client = chromadb.PersistentClient(path=db_path)

        self.collection = self.get_or_create_collection()

    def get_or_create_collection(self):
        """
        Get existing collection or create a new one.

        Returns:
            ChromaDB collection instance
        """
        collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Ayurvedic knowledge base for Sevam"}
        )
        print(f"  Collection '{COLLECTION_NAME}' ready — {collection.count()} docs stored")
        return collection

    def add_documents(self, chunks: List[Dict]) -> None:
        """
        Add document chunks with their embeddings to the vector store.

        Args:
            chunks: List of chunk dicts with keys:
                     chunk_id, embedding, content, title, dosha, category,
                     parent_id, chunk_index
        """
        if not chunks:
            return

        chunk_ids = [c["chunk_id"] for c in chunks]
        embeddings = [c["embedding"] for c in chunks]
        documents = [c["content"] for c in chunks]
        metadatas = [
            {
                "title": c.get("title", ""),
                "dosha": c.get("dosha", ""),
                "category": c.get("category", ""),
                "parent_id": c.get("parent_id", ""),
                "chunk_index": str(c.get("chunk_index", 0)),
                "word_count": str(c.get("word_count", 0)),
            }
            for c in chunks
        ]

        print(f"  Adding {len(chunk_ids)} documents to ChromaDB...")
        self.collection.upsert(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        print(f"  Done. Total stored: {self.collection.count()}")

    def query_similar(
        self,
        query_text: str,
        query_embedding: List[float],
        n_results: int = 3,
        where: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Find the most semantically similar chunks to a query embedding.

        Args:
            query_text: Original query text (for logging)
            query_embedding: Vector of the user query
            n_results: How many top results to return
            where: Optional metadata filter

        Returns:
            List of dicts with keys: content, title, dosha, category, distance
        """
        count = self.collection.count()
        if count == 0:
            return []

        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": min(n_results, count),
            "include": ["documents", "metadatas", "distances"],
        }

        if where:
            query_params["where"] = where

        raw = self.collection.query(**query_params)
        return self._format_results(raw)

    def _format_results(self, raw_results: Dict) -> List[Dict]:
        """
        Format raw ChromaDB results into clean dicts.

        Args:
            raw_results: Raw output from ChromaDB query

        Returns:
            List of formatted result dicts sorted by similarity
        """
        formatted = []

        if not raw_results or not raw_results.get("documents"):
            return formatted

        docs = raw_results["documents"][0]
        metadatas = raw_results["metadatas"][0]
        distances = raw_results["distances"][0]

        for doc, meta, dist in zip(docs, metadatas, distances):
            similarity = round(1 - dist, 4)
            formatted.append({
                "content": doc,
                "title": meta.get("title", "Unknown"),
                "dosha": meta.get("dosha", ""),
                "category": meta.get("category", ""),
                "distance": round(dist, 4),
                "similarity": similarity,
            })

        formatted.sort(key=lambda x: x["similarity"], reverse=True)
        return formatted

    def clear(self) -> None:
        """Delete all documents from the collection. Use carefully."""
        self.client.delete_collection(COLLECTION_NAME)
        self.collection = self.client.get_or_create_collection(name=COLLECTION_NAME)
        print("  Collection cleared.")

    def count(self) -> int:
        """Return number of documents in the collection."""
        return self.collection.count()
