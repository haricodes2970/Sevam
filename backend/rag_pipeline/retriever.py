"""
RAG retriever module.
Takes a user query, embeds it, retrieves relevant medical chunks.
This is what the chatbot calls on every message.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.embeddings.embedder import MedicalEmbedder
from backend.rag_pipeline.vector_store import MedicalVectorStore


class MedicalRetriever:
    """
    Retrieves relevant medical knowledge chunks for a given query.
    Used by the chatbot to ground its responses in real documents.
    """

    def __init__(self):
        """Initialize embedder and vector store."""
        print("  Initializing retriever...")
        self.embedder     = MedicalEmbedder()
        self.vector_store = MedicalVectorStore()
        print("  Retriever ready")

    def retrieve(self, query: str, n_results: int = 3) -> list:
        """
        Retrieve the most relevant medical chunks for a query.

        Args:
            query: User's natural language query or symptom description
            n_results: Number of chunks to retrieve

        Returns:
            List of formatted result dicts sorted by relevance
        """
        if not query or not query.strip():
            return []

        # Embed the query using the same model used for indexing
        query_embedding = self.embedder.embed_text(query)

        # Search ChromaDB for similar chunks
        raw_results = self.vector_store.query(
            query_embedding=query_embedding,
            n_results=n_results
        )

        # Format into clean readable results
        return self.vector_store.format_results(raw_results)

    def retrieve_with_emergency_boost(self, query: str, is_emergency: bool = False) -> list:
        """
        Retrieve chunks, prioritizing emergency documents if needed.

        If the NLP analyzer flagged this as an emergency, we always
        include the emergency warning signs document at the top.

        Args:
            query: User query string
            is_emergency: Whether NLP detected emergency intent

        Returns:
            List of relevant chunks, emergency doc first if applicable
        """
        results = self.retrieve(query, n_results=4)

        if is_emergency:
            # Check if emergency doc is already in results
            has_emergency = any(r.get("source") == "emergency" for r in results)

            if not has_emergency:
                # Retrieve emergency doc specifically
                emergency_results = self.vector_store.query(
                    query_embedding=self.embedder.embed_text("emergency warning signs"),
                    n_results=1,
                    where={"source": "emergency"}
                )
                emergency_chunks = self.vector_store.format_results(emergency_results)
                if emergency_chunks:
                    # Put emergency doc first
                    results = emergency_chunks + results[:3]

        return results


def print_results(results: list, query: str) -> None:
    """Pretty print retrieval results."""
    print(f"\n  Query: '{query}'")
    print(f"  Found {len(results)} relevant chunks:\n")
    for i, r in enumerate(results, 1):
        print(f"  [{i}] {r['title']} (similarity: {r['similarity']})")
        print(f"      Source: {r['source']} | Emergency: {r['is_emergency']}")
        print(f"      Preview: {r['content'][:100]}...")
        print()


if __name__ == "__main__":
    print("🔍 Sevam — RAG Retrieval Test\n")

    retriever = MedicalRetriever()

    test_queries = [
        "I have a severe headache and feel dizzy",
        "my chest hurts when I breathe",
        "I feel tired and weak all the time",
        "sore throat and difficulty swallowing",
    ]

    for query in test_queries:
        results = retriever.retrieve(query, n_results=3)
        print_results(results, query)

    print("✅ Retrieval working! Ready for Phase 4 (LLM chatbot).\n")
