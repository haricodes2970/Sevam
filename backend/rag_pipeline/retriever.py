"""
RAG retriever module for Sevam.
Takes a user query, embeds it, retrieves relevant Ayurvedic knowledge chunks.
This is what the chatbot calls on every message.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.embeddings.embedder import MedicalEmbedder
from backend.rag_pipeline.vector_store import MedicalVectorStore


class MedicalRetriever:
    """
    Retrieves relevant Ayurvedic knowledge chunks for a given query.
    Used by the chatbot to ground its responses in authentic Ayurvedic documents.
    """

    def __init__(self):
        """Initialize embedder and vector store."""
        print("  Initializing retriever...")
        self.embedder = MedicalEmbedder()
        self.vector_store = MedicalVectorStore()
        print("  Retriever ready")

    def retrieve(self, query: str, n_results: int = 3) -> list:
        """
        Retrieve the most relevant Ayurvedic knowledge chunks for a query.

        Args:
            query: User's natural language query or symptom description
            n_results: Number of chunks to retrieve

        Returns:
            List of result dicts with keys: content, title, dosha, category, distance, similarity
        """
        if not query or not query.strip():
            return []

        query_embedding = self.embedder.embed_text(query)

        results = self.vector_store.query_similar(
            query_text=query,
            query_embedding=query_embedding,
            n_results=n_results,
        )

        # Filter out very distant results (lower relevance for short queries).
        max_distance = 1.5
        filtered_results = []
        for result in results:
            dist = result.get("distance")
            if dist is None or dist <= max_distance:
                filtered_results.append(result)

        seen_titles = set()
        unique_results = []
        for result in filtered_results:
            title = result.get("title", "")
            if title not in seen_titles:
                seen_titles.add(title)
                unique_results.append(result)

        return unique_results


def print_results(results: list, query: str) -> None:
    """Pretty print retrieval results."""
    print(f"\n  Query: '{query}'")
    print(f"  Found {len(results)} relevant chunks:\n")
    for i, r in enumerate(results, 1):
        print(f"  [{i}] {r['title']} (similarity: {r['similarity']:.4f})")
        print(f"      Dosha: {r['dosha']} | Category: {r['category']}")
        print(f"      Preview: {r['content'][:120]}...")
        print()


if __name__ == "__main__":
    print("Sevam — RAG Retrieval Test\n")

    retriever = MedicalRetriever()

    test_queries = [
        "I have a bad headache and feel nauseous",
        "feeling very tired and low energy since 3 days",
        "my throat hurts and I have a cough",
    ]

    for query in test_queries:
        results = retriever.retrieve(query, n_results=3)
        print_results(results, query)

    print("Retrieval working! Ready for chatbot integration.\n")
