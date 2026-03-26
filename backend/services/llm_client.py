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
        Generate a response using Groq API (legacy single-string interface).

        The prompt is sent as the user message with a generic Sevam system prompt.
        Prefer generate_chat() for new code which allows a custom system message.

        Args:
            prompt: Full formatted prompt string
            max_tokens: Maximum tokens to generate

        Returns:
            Generated response string
        """
        return self.generate_chat(
            system_message=(
                "You are Sevam, a helpful and responsible Ayurvedic health "
                "companion. Base your answers only on the provided context. "
                "Never give definitive diagnoses. Always recommend consulting "
                "a qualified Ayurvedic practitioner or doctor. "
                "Keep responses clear, empathetic and concise."
            ),
            user_message=prompt,
            max_tokens=max_tokens,
        )

    def generate_chat(
        self,
        system_message: str,
        user_message: str,
        max_tokens: int = 600,
    ) -> str:
        """
        Generate a response using Groq API with explicit system and user messages.

        This is the preferred method for the full pipeline where the system
        message is built by the ContextEngine and prompt builder.

        Args:
            system_message: The system instruction (persona + user context)
            user_message:   The user-side message (RAG context + query)
            max_tokens:     Maximum tokens to generate (default 600)

        Returns:
            Generated response string
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user",   "content": user_message},
                ],
                max_tokens=max_tokens,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()

        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {e}")
