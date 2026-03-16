"""
Database CRUD service layer.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import desc

from backend.models.db_models import (
    Session, Message, SymptomLog, Feedback,
    SeverityEnum, IntentEnum, FeedbackEnum
)


def get_or_create_session(db: DBSession, session_id: str) -> Session:
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        session_uuid = uuid.uuid4()

    session = db.query(Session).filter(Session.id == session_uuid).first()
    if not session:
        session = Session(id=session_uuid)
        db.add(session)
        db.commit()
        db.refresh(session)
    return session


def update_session_activity(db: DBSession, session: Session, had_emergency: bool = False) -> None:
    session.last_active = datetime.now(timezone.utc)
    session.message_count += 1
    if had_emergency:
        session.had_emergency = True
    db.commit()


def save_message(
    db: DBSession,
    session_id: str,
    user_message: str,
    bot_response: str,
    sources: list[str],
    severity: str,
    is_emergency: bool,
) -> Message:
    session = get_or_create_session(db, session_id)

    try:
        severity_enum = SeverityEnum(severity)
    except ValueError:
        severity_enum = SeverityEnum.LOW

    message = Message(
        session_id=session.id,
        user_message=user_message,
        bot_response=bot_response,
        sources_used=", ".join(sources),
        retrieval_count=len(sources),
        severity=severity_enum,
        is_emergency=is_emergency,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    update_session_activity(db, session, had_emergency=is_emergency)
    return message


def save_symptom_log(db: DBSession, message_id: uuid.UUID, nlp_result: dict) -> SymptomLog:
    try:
        intent = IntentEnum(nlp_result.get("intent", "UNKNOWN"))
    except ValueError:
        intent = IntentEnum.UNKNOWN

    log = SymptomLog(
        message_id=message_id,
        intent=intent,
        intent_confidence=nlp_result.get("intent_confidence", 0.0),
        symptoms=", ".join(nlp_result.get("symptoms", [])),
        triggers=", ".join(nlp_result.get("triggers", [])),
        body_parts=", ".join(nlp_result.get("body_parts", [])),
        duration=nlp_result.get("duration"),
        severity_score=nlp_result.get("severity_score", 1),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def save_feedback(db: DBSession, message_id: str, rating: str, comment: Optional[str] = None) -> Optional[Feedback]:
    try:
        msg_uuid = uuid.UUID(message_id)
        rating_enum = FeedbackEnum(rating)
    except ValueError:
        return None

    existing = db.query(Feedback).filter(Feedback.message_id == msg_uuid).first()
    if existing:
        existing.rating = rating_enum
        existing.comment = comment
        db.commit()
        db.refresh(existing)
        return existing

    feedback = Feedback(message_id=msg_uuid, rating=rating_enum, comment=comment)
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def get_recent_sessions(db: DBSession, limit: int = 20) -> list[Session]:
    return db.query(Session).order_by(desc(Session.last_active)).limit(limit).all()


def get_emergency_count(db: DBSession) -> int:
    return db.query(Message).filter(Message.is_emergency == True).count()