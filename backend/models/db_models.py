"""
SQLAlchemy ORM models — 4 tables.
"""

import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Boolean, Integer,
    Float, DateTime, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from backend.database.connection import Base


class SeverityEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EMERGENCY = "EMERGENCY"


class IntentEnum(str, enum.Enum):
    SYMPTOM_ANALYSIS = "SYMPTOM_ANALYSIS"
    EMERGENCY_CHECK = "EMERGENCY_CHECK"
    GENERAL_INFO = "GENERAL_INFO"
    MEDICATION_QUERY = "MEDICATION_QUERY"
    FOLLOWUP = "FOLLOWUP"
    GREETING = "GREETING"
    UNKNOWN = "UNKNOWN"


class FeedbackEnum(str, enum.Enum):
    HELPFUL = "HELPFUL"
    NOT_HELPFUL = "NOT_HELPFUL"
    INACCURATE = "INACCURATE"
    EMERGENCY_MISSED = "EMERGENCY_MISSED"


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_active = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    message_count = Column(Integer, default=0, nullable=False)
    had_emergency = Column(Boolean, default=False, nullable=False)

    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    user_message = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)
    sources_used = Column(Text, default="")
    retrieval_count = Column(Integer, default=0)
    severity = Column(SAEnum(SeverityEnum), default=SeverityEnum.LOW, nullable=False)
    is_emergency = Column(Boolean, default=False, nullable=False)

    session = relationship("Session", back_populates="messages")
    symptom_log = relationship("SymptomLog", back_populates="message", uselist=False, cascade="all, delete-orphan")
    feedback = relationship("Feedback", back_populates="message", uselist=False, cascade="all, delete-orphan")


class SymptomLog(Base):
    __tablename__ = "symptom_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    intent = Column(SAEnum(IntentEnum), default=IntentEnum.UNKNOWN, nullable=False)
    intent_confidence = Column(Float, default=0.0)
    symptoms = Column(Text, default="")
    triggers = Column(Text, default="")
    body_parts = Column(Text, default="")
    duration = Column(String(200), nullable=True)
    severity_score = Column(Integer, default=1)

    message = relationship("Message", back_populates="symptom_log")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message_id = Column(UUID(as_uuid=True), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    rating = Column(SAEnum(FeedbackEnum), nullable=False)
    comment = Column(Text, nullable=True)

    message = relationship("Message", back_populates="feedback")