"""
Prompt builder for Sevam — Ayurvedic RAG responses.

Builds structured (system, user) message pairs for Groq's chat API,
incorporating:
  - User's prakriti and health context (from ContextEngine)
  - Retrieved Ayurvedic knowledge chunks (from RAG)
  - Food-symptom correlation findings (from CorrelationEngine)
  - Conversation history (last 4 turns)
"""

from typing import List, Dict, Optional, Tuple


# ── Ayurvedic persona ─────────────────────────────────────────────────────────

AYURVEDIC_SYSTEM_BASE = """You are Sevam, a knowledgeable and compassionate Ayurvedic health companion.

Your role is to:
- Provide personalised Ayurvedic guidance based on the user's prakriti (body constitution)
- Explain symptoms through the lens of dosha imbalances (Vata, Pitta, Kapha)
- Suggest Ayurvedic dietary and lifestyle remedies grounded in the knowledge provided
- Always recommend consulting a qualified Ayurvedic practitioner or doctor for serious concerns
- Never provide definitive diagnoses or prescribe specific drug dosages

Important rules:
- Base recommendations ONLY on the provided Ayurvedic knowledge context
- If the context does not cover a question, say so honestly
- Keep responses warm, empathetic, clear, and practically useful
- Always close with a recommendation to see a practitioner for persistent or serious symptoms
- Do NOT recommend allergens or substances the user is known to be allergic to"""

MIN_RAG_SIMILARITY = -0.5


def build_ayurvedic_prompt(
    user_message: str,
    system_prefix: str,
    retrieved_chunks: List[Dict],
    food_correlation: Optional[Dict] = None,
    conversation_history: Optional[List[Dict]] = None,
) -> Tuple[str, str]:
    """
    Build a structured (system_message, user_message) pair for Groq's chat API.

    The system message combines the Ayurvedic persona with the user's personal
    context (prakriti, conditions, allergies, food correlation).
    The user message combines the RAG knowledge chunks with conversation history
    and the current query.

    Args:
        user_message:         Current user query (sanitized)
        system_prefix:        Rich context string from ContextEngine — includes
                              prakriti, dosha scores, conditions, allergies,
                              recent food correlation
        retrieved_chunks:     Top RAG chunks from ChromaDB (list of dicts with
                              'title', 'content', 'similarity')
        food_correlation:     Correlation result dict from CorrelationEngine
        conversation_history: Previous turns [{"role": "user"|"assistant",
                              "content": "..."}]

    Returns:
        Tuple of (system_message, user_message) strings ready for Groq API
    """
    # ── System message ────────────────────────────────────────────────────────
    system_parts = [AYURVEDIC_SYSTEM_BASE]
    if system_prefix and system_prefix.strip():
        system_parts.append("\nUSER CONTEXT:\n" + system_prefix)
    system_message = "\n".join(system_parts)

    # ── Ayurvedic knowledge context ───────────────────────────────────────────
    context_parts: List[str] = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        if chunk.get("similarity", 0) >= MIN_RAG_SIMILARITY:
            dosha_tag = f" [{chunk['dosha']}]" if chunk.get("dosha") else ""
            context_parts.append(
                f"[Ayurvedic Knowledge {i}: {chunk['title']}{dosha_tag}]\n"
                f"{chunk['content']}"
            )

    context_block = (
        "\n\n".join(context_parts)
        if context_parts
        else "No specific Ayurvedic knowledge retrieved for this query."
    )

    # ── Food correlation block ────────────────────────────────────────────────
    correlation_block = ""
    if food_correlation and food_correlation.get("has_correlation"):
        trigger = food_correlation.get("likely_trigger", "")
        dosha = food_correlation.get("dosha_aggravated", "")
        explanation = food_correlation.get("explanation", "")
        advice = food_correlation.get("dietary_advice", "")
        correlation_block = (
            f"\nFOOD-SYMPTOM CORRELATION DETECTED:\n"
            f"Trigger: {trigger}\n"
            f"Dosha aggravated: {dosha}\n"
            f"Explanation: {explanation}\n"
            f"Dietary advice: {advice}"
        )

    # ── Conversation history ──────────────────────────────────────────────────
    history_block = ""
    if conversation_history:
        lines = []
        for turn in conversation_history[-4:]:  # last 4 turns only
            role = turn.get("role", "")
            content = turn.get("content", "")
            if role == "user":
                lines.append(f"User: {content}")
            elif role == "assistant":
                lines.append(f"Sevam: {content}")
        if lines:
            history_block = "\nCONVERSATION HISTORY:\n" + "\n".join(lines)

    # ── Assemble user-side message ────────────────────────────────────────────
    user_msg = (
        f"AYURVEDIC KNOWLEDGE BASE:\n{context_block}"
        f"{correlation_block}"
        f"{history_block}"
        f"\n\nUser question: {user_message}"
        f"\n\nPlease provide personalised Ayurvedic guidance based on the user's "
        f"constitution and the knowledge above."
    )

    return system_message, user_msg


# ── Legacy helpers (kept for backward compatibility) ──────────────────────────

def build_rag_prompt(
    user_message: str,
    retrieved_chunks: List[Dict],
    conversation_history: Optional[List[Dict]] = None,
) -> str:
    """
    Legacy single-string prompt builder (Mistral-style [INST] format).
    Kept so any existing callers don't break.

    Args:
        user_message: Current user query
        retrieved_chunks: Top chunks from ChromaDB retrieval
        conversation_history: Previous turns in the conversation

    Returns:
        Fully formatted prompt string
    """
    context_parts = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        if chunk.get("similarity", 0) >= MIN_RAG_SIMILARITY:
            context_parts.append(
                f"[Source {i}: {chunk['title']}]\n{chunk['content']}"
            )

    context_block = (
        "\n\n".join(context_parts)
        if context_parts
        else "No specific medical context found."
    )

    history_block = ""
    if conversation_history:
        for turn in conversation_history[-4:]:
            role = turn.get("role", "")
            content = turn.get("content", "")
            if role == "user":
                history_block += f"\nUser: {content}"
            elif role == "assistant":
                history_block += f"\nSevam: {content}"

    return (
        f"<s>[INST] {AYURVEDIC_SYSTEM_BASE}\n\n"
        f"MEDICAL CONTEXT:\n{context_block}"
        f"{history_block}\n\n"
        f"User question: {user_message}\n\n"
        f"Please provide a helpful, safe, and grounded response based on the "
        f"medical context above. [/INST]"
    )


def build_general_prompt(user_message: str) -> str:
    """
    Legacy single-string prompt for general (non-symptom) questions.

    Args:
        user_message: User query string

    Returns:
        Formatted prompt string
    """
    return (
        f"<s>[INST] {AYURVEDIC_SYSTEM_BASE}\n\n"
        f"User question: {user_message}\n\n"
        f"Please provide a helpful response. If this is a medical question, "
        f"remind the user to consult a healthcare professional. [/INST]"
    )
