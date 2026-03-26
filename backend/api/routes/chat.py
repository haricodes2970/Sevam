"""
Chat endpoint — accepts user messages and returns personalised Ayurvedic guidance.

Full pipeline per request:
  user message → safety guard → context engine → RAG → Groq LLM → save → respond
"""

import uuid
import logging
from fastapi import APIRouter, HTTPException

from backend.models.schemas import ChatRequest, ChatResponse, SeverityLevel
from backend.services import db_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Lazy-loaded singleton chatbot (initialised on first request)
_chatbot = None


def _get_chatbot():
    """Lazy-load SevamChatbot to avoid heavy initialisation at server startup."""
    global _chatbot
    if _chatbot is None:
        try:
            from backend.services.chatbot import SevamChatbot
            _chatbot = SevamChatbot()
        except Exception as exc:
            logger.error("Chatbot init failed: %s", exc)
            raise HTTPException(status_code=503, detail=f"Chatbot unavailable: {exc}")
    return _chatbot


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a user message through the full Sevam pipeline and return
    personalised Ayurvedic guidance.

    Pipeline:
    1. Load or create session
    2. Safety guard (emergency detection)
    3. Context engine (prakriti + food logs + correlation)
    4. RAG retrieval (Ayurvedic knowledge chunks)
    5. Groq LLM generation
    6. Save exchange to MongoDB
    7. Return enriched response

    The session_id is auto-generated if not supplied.
    Providing an existing session_id links messages to the same session.
    """
    chatbot = _get_chatbot()
    session_id = request.session_id or str(uuid.uuid4())
    user_id = request.user_id or "anonymous"

    # ── Run the full async pipeline ───────────────────────────────────────────
    try:
        result = await chatbot.chat(
            user_id=user_id,
            message=request.message,
            session_id=session_id,
        )
    except Exception as exc:
        logger.error("Chat pipeline failed for user %s: %s", user_id, exc)
        raise HTTPException(status_code=500, detail=f"Chat failed: {exc}")

    # ── Parse severity ────────────────────────────────────────────────────────
    try:
        severity = SeverityLevel(result.get("severity", "LOW"))
    except ValueError:
        severity = SeverityLevel.LOW

    # ── Persist to MongoDB (non-fatal if it fails) ────────────────────────────
    try:
        await db_service.save_message(
            session_id=session_id,
            user_id=user_id,
            user_message=request.message,
            bot_response=result.get("response", ""),
            sources=result.get("sources", []),
            severity=severity.value,
            is_emergency=result.get("is_emergency", False),
        )
    except Exception as db_exc:
        logger.warning("DB save failed (non-fatal) for session %s: %s", session_id, db_exc)

    # ── Build and return response ─────────────────────────────────────────────
    sources = list(dict.fromkeys(result.get("sources", [])))
    return ChatResponse(
        response=result.get("response", ""),
        sources=sources,
        severity=severity,
        is_emergency=result.get("is_emergency", False),
        session_id=session_id,
        food_correlation=result.get("food_correlation", {}),
        prakriti=result.get("prakriti", "Unknown"),
    )
