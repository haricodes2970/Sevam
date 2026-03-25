"""
Vector store module using ChromaDB.
Stores and retrieves medical document embeddings.
"""

import chromadb
from chromadb.config import Settings
import os
from typing import List, Dict


CHROMA_DB_PATH = "./data/vector_db"
COLLECTION_NAME = "medical_knowledge"


class MedicalVectorStore:
    """
    Manages the ChromaDB vector database for medical knowledge.
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

        # Get or create the medical knowledge collection
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Medical knowledge base for Sevam"}
        )
        print(f"  Collection '{COLLECTION_NAME}' ready — {self.collection.count()} docs stored")

    def add_documents(
        self,
        chunk_ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict]
    ) -> None:
        """
        Add document chunks with their embeddings to the vector store.

        Args:
            chunk_ids: Unique ID for each chunk
            embeddings: Vector embedding for each chunk
            documents: Raw text content for each chunk
            metadatas: Metadata dict for each chunk (title, source, etc.)
        """
        print(f"  Adding {len(chunk_ids)} documents to ChromaDB...")

        # ChromaDB upsert — adds new or updates existing
        self.collection.upsert(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        print(f"  Done. Total stored: {self.collection.count()}")

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Dict = None
    ) -> Dict:
        """
        Find the most semantically similar chunks to a query embedding.

        Args:
            query_embedding: Vector of the user query
            n_results: How many top results to return
            where: Optional metadata filter (e.g. {"source": "emergency"})

        Returns:
            ChromaDB results dict with documents, metadatas, distances
        """
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": min(n_results, self.collection.count()),
            "include": ["documents", "metadatas", "distances"]
        }

        if where:
            query_params["where"] = where

        return self.collection.query(**query_params)

    def format_results(self, raw_results: Dict) -> List[Dict]:
        """
        Format raw ChromaDB results into clean readable dicts.

        Args:
            raw_results: Raw output from ChromaDB query

        Returns:
            List of formatted result dicts with score, title, content
        """
        formatted = []

        if not raw_results or not raw_results.get("documents"):
            return formatted

        docs      = raw_results["documents"][0]
        metadatas = raw_results["metadatas"][0]
        distances = raw_results["distances"][0]

        for doc, meta, dist in zip(docs, metadatas, distances):
            # Convert distance to similarity score (lower distance = higher similarity)
            similarity = round(1 - dist, 4)
            formatted.append({
                "title":      meta.get("title", "Unknown"),
                "source":     meta.get("source", "Unknown"),
                "content":    doc,
                "similarity": similarity,
                "is_emergency": meta.get("is_emergency", False),
            })

        # Sort by similarity descending
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
