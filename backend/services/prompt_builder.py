"""
Prompt builder for medical RAG responses.
Constructs safe, grounded prompts using retrieved medical context.
"""

from typing import List, Dict


SYSTEM_PROMPT = """You are Sevam, a helpful and responsible medical information assistant.

Your role is to:
- Help users understand their symptoms using the medical knowledge provided
- Explain possible causes based ONLY on the provided medical context
- Always recommend consulting a healthcare professional
- Never provide definitive diagnoses
- Always mention emergency warning signs when relevant

Important rules:
- Base your response ONLY on the provided medical context below
- If the context does not cover the question, say so honestly
- Keep responses clear, empathetic, and easy to understand
- Always end with a recommendation to see a doctor for proper evaluation"""


def build_rag_prompt(
    user_message: str,
    retrieved_chunks: List[Dict],
    conversation_history: List[Dict] = None
) -> str:
    """
    Build a complete RAG prompt with medical context.

    The prompt structure is:
    1. System instructions (who Sevam is)
    2. Retrieved medical context (grounding)
    3. Conversation history (memory)
    4. Current user message

    Args:
        user_message: Current user query
        retrieved_chunks: Top chunks from ChromaDB retrieval
        conversation_history: Previous turns in the conversation

    Returns:
        Fully formatted prompt string for Mistral-7B
    """

    # Build context block from retrieved chunks
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        if chunk.get("similarity", 0) > 0:  # Only use positively similar chunks
            context_parts.append(
                f"[Source {i}: {chunk['title']}]\n{chunk['content']}"
            )

    context_block = "\n\n".join(context_parts) if context_parts else "No specific medical context found."

    # Build conversation history block
    history_block = ""
    if conversation_history:
        for turn in conversation_history[-4:]:  # Last 4 turns only
            role = turn.get("role", "")
            content = turn.get("content", "")
            if role == "user":
                history_block += f"\nUser: {content}"
            elif role == "assistant":
                history_block += f"\nSevam: {content}"

    # Assemble final Mistral-style prompt
    prompt = f"""<s>[INST] {SYSTEM_PROMPT}

MEDICAL CONTEXT:
{context_block}
{history_block}

User question: {user_message}

Please provide a helpful, safe, and grounded response based on the medical context above. [/INST]"""

    return prompt


def build_general_prompt(user_message: str) -> str:
    """
    Build a prompt for general (non-symptom) questions.
    Used when intent is GENERAL_INFO or GREETING.

    Args:
        user_message: User query string

    Returns:
        Formatted prompt string
    """
    return f"""<s>[INST] {SYSTEM_PROMPT}

User question: {user_message}

Please provide a helpful response. If this is a medical question,
remind the user to consult a healthcare professional. [/INST]"""
