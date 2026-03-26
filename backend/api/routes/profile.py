"""
User profile routes for Sevam — Phase 8D.

Endpoints:
    GET  /profile/questions              20-question dosha questionnaire
    POST /profile/calculate-dosha        Score answers → prakriti result
    POST /profile/create                 Create full user profile
    GET  /profile/{user_id}              Retrieve full profile
    PUT  /profile/{user_id}              Partial update of profile fields
    GET  /profile/{user_id}/prakriti     Quick prakriti + recommendations
"""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.dosha_calculator import DoshaCalculator
from backend.services.db_service import (
    create_user_profile,
    get_user_profile,
    update_user_profile_fields,
    update_dosha,
    check_user_exists,
)
from backend.models.db_models import HealthProfile

router = APIRouter(prefix="/profile", tags=["Profile"])

_calc = DoshaCalculator()


# ── Request / Response schemas ────────────────────────────────────────────────

class DoshaAnswersRequest(BaseModel):
    """Request body for /calculate-dosha."""
    answers: dict[str, str] = Field(
        ...,
        description="Mapping of question_id (str) → option key ('a'/'b'/'c')",
        example={"1": "b", "2": "b", "3": "b"},
    )


class HealthProfileIn(BaseModel):
    """Health profile sub-object accepted in POST /create and PUT /{user_id}."""
    conditions: list[str] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    lifestyle: str = ""
    sleep_hours: float = 0.0
    stress_level: str = ""
    activity_level: str = ""


class CreateProfileRequest(BaseModel):
    """Request body for POST /profile/create."""
    user_id: str
    name: str = ""
    age: Optional[int] = None
    gender: str = ""
    prakriti: str = "Unknown"
    dosha_scores: dict[str, Any] = Field(default_factory=dict)
    dosha_percentages: dict[str, Any] = Field(default_factory=dict)
    health_profile: HealthProfileIn = Field(default_factory=HealthProfileIn)


class UpdateProfileRequest(BaseModel):
    """Request body for PUT /profile/{user_id}. All fields optional."""
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    prakriti: Optional[str] = None
    dosha_scores: Optional[dict[str, Any]] = None
    dosha_percentages: Optional[dict[str, Any]] = None
    health_profile: Optional[HealthProfileIn] = None
    onboarding_complete: Optional[bool] = None


# ── GET /profile/questions ────────────────────────────────────────────────────

@router.get("/questions")
async def get_dosha_questions():
    """Return all 20 dosha questionnaire questions for frontend rendering.

    Each question contains an id, category, question text, and three options
    (a/b/c) with display text. The dosha mapping is intentionally hidden.
    """
    questions = _calc.get_questions()
    return {"count": len(questions), "questions": questions}


# ── POST /profile/calculate-dosha ─────────────────────────────────────────────

@router.post("/calculate-dosha")
async def calculate_dosha(req: DoshaAnswersRequest):
    """Score a completed questionnaire and return the prakriti result.

    Accepts a dict of {question_id: option} answers.  Returns the dominant
    dosha, raw scores, percentages, a description, and lifestyle recommendations.
    """
    result = _calc.calculate_prakriti(req.answers)
    return result


# ── POST /profile/create ──────────────────────────────────────────────────────

@router.post("/create", status_code=201)
async def create_profile(req: CreateProfileRequest):
    """Create a full user profile after completing the onboarding questionnaire.

    If a profile already exists for the given user_id a 409 is returned.
    """
    exists = await check_user_exists(req.user_id)
    if exists:
        raise HTTPException(
            status_code=409,
            detail=f"Profile for user '{req.user_id}' already exists. Use PUT to update.",
        )

    hp = HealthProfile(**req.health_profile.model_dump())

    profile_data = {
        "user_id": req.user_id,
        "name": req.name,
        "age": req.age,
        "gender": req.gender,
        "prakriti": req.prakriti,
        "dosha_scores": req.dosha_scores,
        "dosha_percentages": req.dosha_percentages,
        "health_profile": hp.model_dump(),
        "onboarding_complete": True,
    }

    uid = await create_user_profile(profile_data)
    return {"user_id": uid, "message": "Profile created"}


# ── GET /profile/{user_id} ────────────────────────────────────────────────────

@router.get("/{user_id}")
async def get_profile(user_id: str):
    """Retrieve a user's full profile by user_id.

    Returns 404 if no profile is found.
    """
    profile = await get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile not found for user '{user_id}'")
    return profile.model_dump()


# ── PUT /profile/{user_id} ────────────────────────────────────────────────────

@router.put("/{user_id}")
async def update_profile(user_id: str, req: UpdateProfileRequest):
    """Partially update a user profile.  Only non-None fields are written.

    Returns 404 if the profile does not exist.
    """
    exists = await check_user_exists(user_id)
    if not exists:
        raise HTTPException(status_code=404, detail=f"Profile not found for user '{user_id}'")

    updates: dict[str, Any] = {}
    for field in ("name", "age", "gender", "prakriti", "dosha_scores",
                  "dosha_percentages", "onboarding_complete"):
        val = getattr(req, field, None)
        if val is not None:
            updates[field] = val

    if req.health_profile is not None:
        updates["health_profile"] = req.health_profile.model_dump()

    if not updates:
        return {"message": "No changes provided", "user_id": user_id}

    modified = await update_user_profile_fields(user_id, updates)
    if not modified:
        return {"message": "No fields changed", "user_id": user_id}

    return {"message": "Profile updated", "user_id": user_id}


# ── GET /profile/{user_id}/prakriti ──────────────────────────────────────────

@router.get("/{user_id}/prakriti")
async def get_prakriti(user_id: str):
    """Return just the prakriti and dosha recommendations for a user.

    Useful for lightweight widgets or quick access without the full profile.
    Returns 404 if the profile does not exist.
    """
    profile = await get_user_profile(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile not found for user '{user_id}'")

    # Re-derive recommendations from the calculator for consistency
    prakriti_label = profile.prakriti
    dominant = prakriti_label.split("-")[0] if "-" in prakriti_label else prakriti_label
    recommendations = _calc._RECOMMENDATIONS.get(
        dominant,
        {
            "diet": "Follow a balanced diet suitable to your constitution.",
            "lifestyle": "Maintain a regular daily routine.",
            "avoid": "Consult an Ayurvedic practitioner for personalised guidance.",
        },
    )
    description = _calc._DESCRIPTIONS.get(
        prakriti_label, _calc._DESCRIPTIONS.get(dominant, "")
    )

    return {
        "user_id": user_id,
        "prakriti": prakriti_label,
        "dosha_scores": profile.dosha_scores,
        "dosha_percentages": profile.dosha_percentages,
        "prakriti_description": description,
        "recommendations": recommendations,
    }
