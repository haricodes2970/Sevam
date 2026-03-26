"""
Pydantic request and response schemas for SympDecoder API.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum


class SeverityLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EMERGENCY = "EMERGENCY"


class IntentType(str, Enum):
    SYMPTOM_ANALYSIS = "SYMPTOM_ANALYSIS"
    EMERGENCY_CHECK = "EMERGENCY_CHECK"
    GENERAL_INFO = "GENERAL_INFO"
    MEDICATION_QUERY = "MEDICATION_QUERY"
    FOLLOWUP = "FOLLOWUP"
    GREETING = "GREETING"
    UNKNOWN = "UNKNOWN"


class ChatRequest(BaseModel):
    """Request body for POST /chat."""
    user_id: str = Field(default="anonymous", description="User identifier")
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = Field(default=None)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message cannot be blank")
        return v.strip()


class ChatResponse(BaseModel):
    """Response from POST /chat."""
    response: str
    sources: list[str] = Field(default_factory=list)
    severity: SeverityLevel
    is_emergency: bool
    session_id: Optional[str] = Field(default=None)
    food_correlation: dict = Field(default_factory=dict)
    prakriti: str = Field(default="Unknown")


class SymptomAnalysisRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message cannot be blank")
        return v.strip()


class SymptomAnalysisResponse(BaseModel):
    original_message: str
    intent: IntentType
    intent_confidence: float
    symptoms: list[str]
    triggers: list[str]
    duration: Optional[str]
    body_parts: list[str]
    severity: SeverityLevel
    severity_score: int
    severity_indicators: list[str]
    is_emergency: bool


class KnowledgeSource(BaseModel):
    chunk_id: str
    parent_id: str
    title: str
    source: str
    chunk_index: int
    total_chunks: int
    word_count: int
    is_emergency: bool


class KnowledgeSourcesResponse(BaseModel):
    total: int
    sources: list[KnowledgeSource]


class ServiceStatus(BaseModel):
    status: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict[str, ServiceStatus]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: int