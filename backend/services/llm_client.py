"""
LLM client using Groq API.
Groq provides free, fast access to Llama 3 — no credit card needed.
Much more reliable than HuggingFace free tier.
"""

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Llama 3.1 8B — fast, free, great for medical Q&A
MODEL_ID = "llama-3.1-8b-instant"


class HuggingFaceLLM:
    """
    LLM client using Groq's free API.
    Class name kept as HuggingFaceLLM so no other files need changing.
    """

    def __init__(self):
        """Initialize Groq client."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")

        self.client = Groq(api_key=api_key)
        self.model_id = MODEL_ID
        print(f"  LLM client ready: {MODEL_ID} via Groq")

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """
        Generate a response using Groq API.

        Args:
            prompt: Full formatted prompt string
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response string
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are Sevam, a helpful and responsible medical "
                            "information assistant. Base your answers only on the "
                            "provided medical context. Never give definitive diagnoses. "
                            "Always recommend consulting a qualified doctor. "
                            "Keep responses clear, empathetic and concise."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=max_tokens,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}")
