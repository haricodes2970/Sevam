"""
Food log routes for Sevam.

Endpoints for logging meals, retrieving food history, and deleting logs.
Each logged meal is analyzed for Ayurvedic food qualities.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.food_analyzer import FoodAnalyzer
from backend.services.db_service import (
    save_food_log,
    get_recent_food_logs,
    get_today_food_logs,
    delete_food_log,
)
from backend.models.db_models import FoodQualities

router = APIRouter(prefix="/food-log", tags=["Food Log"])

# Shared analyzer instance
_analyzer = FoodAnalyzer()


# ── Request / Response models ────────────────────────────────────────────────

class FoodLogRequest(BaseModel):
    """Request body for creating a food log entry."""
    user_id: str
    raw_text: str
    meal_type: str = Field(default="snack", pattern="^(breakfast|lunch|dinner|snack)$")


class FoodLogResponse(BaseModel):
    """Response after creating a food log entry."""
    log_id: str
    message: str
    analysis: dict
    ayurvedic_summary: str


# ── POST /food-log ───────────────────────────────────────────────────────────

@router.post("", response_model=FoodLogResponse)
async def create_food_log(req: FoodLogRequest):
    """
    Log a meal and get Ayurvedic food quality analysis.

    Analyzes the food description, determines Ayurvedic qualities
    (hot/cold, heavy/light, spicy/bland, dosha impact), and saves to MongoDB.
    """
    analysis = _analyzer.analyze(req.raw_text)

    qualities = FoodQualities(
        hot_cold=analysis["qualities"]["hot_cold"],
        heavy_light=analysis["qualities"]["heavy_light"],
        spicy_bland=analysis["qualities"]["spicy_bland"],
        oily_dry=analysis["qualities"]["oily_dry"],
        dosha_impact=analysis["qualities"]["dosha_impact"],
    )

    log = await save_food_log(
        user_id=req.user_id,
        raw_text=req.raw_text,
        meal_type=req.meal_type,
        food_qualities=qualities,
    )

    return FoodLogResponse(
        log_id=log.log_id,
        message="Food log saved",
        analysis=analysis["qualities"],
        ayurvedic_summary=analysis["ayurvedic_summary"],
    )


# ── GET /food-log/{user_id} ─────────────────────────────────────────────────

@router.get("/{user_id}")
async def get_user_food_logs(user_id: str):
    """
    Get the last 7 days of food logs for a user.

    Returns a list of food log entries ordered by most recent first.
    """
    logs = await get_recent_food_logs(user_id, days=7)
    return {
        "user_id": user_id,
        "count": len(logs),
        "logs": [log.model_dump() for log in logs],
    }


# ── GET /food-log/{user_id}/today ────────────────────────────────────────────

@router.get("/{user_id}/today")
async def get_user_today_logs(user_id: str):
    """
    Get today's food logs for a user.

    Returns food log entries from the current day only.
    """
    logs = await get_today_food_logs(user_id)
    return {
        "user_id": user_id,
        "count": len(logs),
        "logs": [log.model_dump() for log in logs],
    }


# ── DELETE /food-log/{log_id} ────────────────────────────────────────────────

@router.delete("/{log_id}")
async def remove_food_log(log_id: str):
    """
    Delete a specific food log entry by its log_id.

    Returns 404 if the log is not found.
    """
    deleted = await delete_food_log(log_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Food log not found")
    return {"message": "Food log deleted", "log_id": log_id}
