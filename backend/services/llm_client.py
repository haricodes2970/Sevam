"""
Sevam — LLM Client
Uses Ollama local LLM (llama3.2) for zero API cost and full privacy.
"""

import ollama
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

print(f"[OK] Ollama LLM ready -> model: {OLLAMA_MODEL}")


def generate_chat(system_message: str, user_message: str) -> str:
    """Generate response using Ollama local LLM."""
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Ollama error: {str(e)}. Make sure Ollama is running."


def generate(prompt: str) -> str:
    """Legacy method — delegates to generate_chat."""
    return generate_chat(
        system_message="You are Sevam, a personalized Ayurvedic health companion.",
        user_message=prompt
    )
