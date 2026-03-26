"""
Pydantic models for Sevam's MongoDB collections.

Each model mirrors one collection document. Motor stores/retrieves plain dicts;
call .model_dump() before inserting and Model(**doc) after reading.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field


# ── Helpers ───────────────────────────────────────────────────────────────────

def _new_uuid() -> str:
    """Return a fresh UUID4 string."""
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    """Return the current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)


# ── 1. users ──────────────────────────────────────────────────────────────────

class DoshaScores(BaseModel):
    """Relative strength of each Ayurvedic dosha (0.0–100.0)."""
    vata: float = 0.0
    pitta: float = 0.0
    kapha: float = 0.0


class HealthProfile(BaseModel):
    """Health metadata collected during onboarding or conversation."""
    conditions: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    lifestyle: str = ""
    sleep_hours: float = 0.0
    stress_level: str = ""
    activity_level: str = ""


class UserModel(BaseModel):
    """Document schema for the *users* collection."""
    user_id: str = Field(default_factory=_new_uuid)
    created_at: datetime = Field(default_factory=_utcnow)
    prakriti: str = "Unknown"
    dosha_scores: DoshaScores = Field(default_factory=DoshaScores)
    health_profile: HealthProfile = Field(default_factory=HealthProfile)


# ── 1b. user_profiles (full onboarding profile) ───────────────────────────────

class UserProfile(BaseModel):
    """Full onboarding profile stored in the *user_profiles* collection.

    Created once during the dosha questionnaire flow and updated on PUT.
    """

    user_id: str
    name: str = ""
    age: Optional[int] = None
    gender: str = ""
    created_at: datetime = Field(default_factory=_utcnow)
    prakriti: str = "Unknown"
    dosha_scores: dict[str, Any] = Field(default_factory=dict)
    dosha_percentages: dict[str, Any] = Field(default_factory=dict)
    health_profile: HealthProfile = Field(default_factory=HealthProfile)
    onboarding_complete: bool = False


# ── 2. sessions ───────────────────────────────────────────────────────────────

class SessionModel(BaseModel):
    """Document schema for the *sessions* collection."""
    session_id: str = Field(default_factory=_new_uuid)
    user_id: str
    created_at: datetime = Field(default_factory=_utcnow)
    message_count: int = 0
    is_emergency: bool = False


# ── 3. messages ───────────────────────────────────────────────────────────────

class MessageModel(BaseModel):
    """Document schema for the *messages* collection."""
    message_id: str = Field(default_factory=_new_uuid)
    session_id: str
    user_id: str
    timestamp: datetime = Field(default_factory=_utcnow)
    user_message: str
    bot_response: str
    sources: list[str] = Field(default_factory=list)
    severity: str = "LOW"
    is_emergency: bool = False


# ── 4. food_logs ──────────────────────────────────────────────────────────────

class FoodQualities(BaseModel):
    """Ayurvedic quality breakdown for a logged food item."""
    hot_cold: Optional[str] = None        # "hot" | "cold" | "neutral"
    heavy_light: Optional[str] = None     # "heavy" | "light"
    spicy_bland: Optional[str] = None     # "spicy" | "bland"
    oily_dry: Optional[str] = None        # "oily" | "dry"
    dosha_impact: dict = Field(default_factory=dict)  # {"vata": "aggravates", ...}


class FoodLogModel(BaseModel):
    """Document schema for the *food_logs* collection."""
    log_id: str = Field(default_factory=_new_uuid)
    user_id: str
    timestamp: datetime = Field(default_factory=_utcnow)
    raw_text: str
    meal_type: Literal["breakfast", "lunch", "dinner", "snack"] = "snack"
    food_qualities: FoodQualities = Field(default_factory=FoodQualities)


# ── 5. feedback ───────────────────────────────────────────────────────────────

class FeedbackModel(BaseModel):
    """Document schema for the *feedback* collection."""
    feedback_id: str = Field(default_factory=_new_uuid)
    session_id: str
    message_id: str
    rating: Literal["HELPFUL", "NOT_HELPFUL", "INACCURATE", "EMERGENCY_MISSED"]
    created_at: datetime = Field(default_factory=_utcnow)
