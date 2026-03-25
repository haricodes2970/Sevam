"""
Embedding engine for Sevam.
Converts text into vector representations using SentenceTransformers.
The same model must be used for both indexing and querying.
"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np


# Using a small but powerful model — good balance of speed and accuracy
MODEL_NAME = "all-MiniLM-L6-v2"


class MedicalEmbedder:
    """
    Wraps SentenceTransformer to generate embeddings for medical text.
    Loaded once and reused — loading is expensive.
    """

    def __init__(self, model_name: str = MODEL_NAME):
        """
        Initialize the embedder with a SentenceTransformer model.

        Args:
            model_name: HuggingFace model name to use
        """
        print(f"  Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        print(f"  Embedding model ready")

    def embed_text(self, text: str) -> List[float]:
        """
        Embed a single text string into a vector.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")

        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """
        Embed a list of texts efficiently in batches.
        Batching is faster than embedding one by one.

        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process at once

        Returns:
            List of embedding vectors
        """
        if not texts:
            return []

        print(f"  Embedding {len(texts)} texts in batches of {batch_size}...")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings.tolist()

    def get_embedding_dimension(self) -> int:
        """Return the dimension size of this model's embeddings."""
        return self.model.get_sentence_embedding_dimension()
