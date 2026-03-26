"""
Chat endpoint — accepts user messages and returns Ayurvedic health guidance.
"""

import uuid
from fastapi import APIRouter, HTTPException

from backend.models.schemas import ChatRequest, ChatResponse, SeverityLevel
from backend.services import db_service

router = APIRouter()

_chatbot = None


def _get_chatbot():
    """Lazy-load the chatbot to avoid import overhead at startup."""
    global _chatbot
    if _chatbot is None:
        try:
            from backend.services.chatbot import SevamChatbot
            _chatbot = SevamChatbot()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Chatbot unavailable: {str(e)}")
    return _chatbot


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a user message and return a Sevam bot response.

    Saves the exchange to MongoDB after responding.
    A missing or blank session_id generates a new session UUID.
    """
    chatbot = _get_chatbot()
    session_id = request.session_id or str(uuid.uuid4())
    # Use a placeholder user_id until auth is implemented
    user_id = "anonymous"

    try:
        result = chatbot.chat(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

    try:
        severity = SeverityLevel(result.get("severity", "LOW"))
    except ValueError:
        severity = SeverityLevel.LOW

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
    except Exception as db_error:
        print(f"[warn] DB save failed (non-fatal): {db_error}")

    return ChatResponse(
        response=result.get("response", ""),
        sources=result.get("sources", []),
        severity=severity,
        is_emergency=result.get("is_emergency", False),
        session_id=session_id,
    )
