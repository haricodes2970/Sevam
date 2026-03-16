import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session as DBSession

from backend.models.schemas import ChatRequest, ChatResponse, SeverityLevel
from backend.database.connection import get_db
from backend.services.db_service import save_message, save_symptom_log

router = APIRouter()

_chatbot = None


def _get_chatbot():
    global _chatbot
    if _chatbot is None:
        try:
            from backend.services.chatbot import MedicNightChatbot
            _chatbot = MedicNightChatbot()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Chatbot unavailable: {str(e)}")
    return _chatbot


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest, db: DBSession = Depends(get_db)) -> ChatResponse:
    chatbot = _get_chatbot()
    session_id = request.session_id or str(uuid.uuid4())

    try:
        result = chatbot.chat(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

    try:
        severity = SeverityLevel(result.get("severity", "LOW"))
    except ValueError:
        severity = SeverityLevel.LOW

    try:
        saved_message = save_message(
            db=db,
            session_id=session_id,
            user_message=request.message,
            bot_response=result.get("response", ""),
            sources=result.get("sources", []),
            severity=severity.value,
            is_emergency=result.get("is_emergency", False),
        )
        if "analysis" in result:
            save_symptom_log(db=db, message_id=saved_message.id, nlp_result=result["analysis"])
    except Exception as db_error:
        print(f"⚠️  DB save failed (non-fatal): {db_error}")

    return ChatResponse(
        response=result.get("response", ""),
        sources=result.get("sources", []),
        severity=severity,
        is_emergency=result.get("is_emergency", False),
        session_id=session_id,
    )