from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel, Field
from typing import Optional

from backend.database.connection import get_db
from backend.services.db_service import save_feedback

router = APIRouter()


class FeedbackRequest(BaseModel):
    message_id: str = Field(..., description="UUID of the message to rate")
    rating: str = Field(..., description="HELPFUL | NOT_HELPFUL | INACCURATE | EMERGENCY_MISSED")
    comment: Optional[str] = Field(default=None, max_length=500)


class FeedbackResponse(BaseModel):
    success: bool
    message: str


@router.post("/feedback", response_model=FeedbackResponse, tags=["Feedback"])
async def submit_feedback(request: FeedbackRequest, db: DBSession = Depends(get_db)) -> FeedbackResponse:
    valid_ratings = {"HELPFUL", "NOT_HELPFUL", "INACCURATE", "EMERGENCY_MISSED"}
    if request.rating not in valid_ratings:
        raise HTTPException(status_code=422, detail=f"Invalid rating. Must be one of: {valid_ratings}")

    result = save_feedback(db=db, message_id=request.message_id, rating=request.rating, comment=request.comment)
    if not result:
        raise HTTPException(status_code=404, detail="Message not found or invalid message_id")

    return FeedbackResponse(success=True, message="Feedback saved. Thank you!")