"""
Feedback endpoint — lets users rate individual bot responses.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from backend.services import db_service

router = APIRouter()

VALID_RATINGS = {"HELPFUL", "NOT_HELPFUL", "INACCURATE", "EMERGENCY_MISSED"}


class FeedbackRequest(BaseModel):
    session_id: str = Field(..., description="UUID of the session")
    message_id: str = Field(..., description="UUID of the message to rate")
    rating: str = Field(..., description="HELPFUL | NOT_HELPFUL | INACCURATE | EMERGENCY_MISSED")


class FeedbackResponse(BaseModel):
    success: bool
    message: str


@router.post("/feedback", response_model=FeedbackResponse, tags=["Feedback"])
async def submit_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """Save user feedback on a bot message.

    Validates the rating value and persists to the feedback collection.
    """
    if request.rating not in VALID_RATINGS:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid rating. Must be one of: {VALID_RATINGS}",
        )

    await db_service.save_feedback(
        session_id=request.session_id,
        message_id=request.message_id,
        rating=request.rating,
    )

    return FeedbackResponse(success=True, message="Feedback saved. Thank you!")
