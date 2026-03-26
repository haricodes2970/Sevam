"""
Async CRUD service layer for Sevam's 5 MongoDB collections.

All functions are async and use Motor via get_database().
Exceptions are logged and re-raised so callers can decide how to handle them.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

from backend.database.connection import get_database
from backend.models.db_models import (
    UserModel,
    UserProfile,
    SessionModel,
    MessageModel,
    FoodLogModel,
    FeedbackModel,
    DoshaScores,
    HealthProfile,
    FoodQualities,
)

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── 1. users ──────────────────────────────────────────────────────────────────

async def create_user(user_id: str) -> UserModel:
    """Insert a new user document into the *users* collection.

    Args:
        user_id: Caller-supplied UUID string (typically from the frontend).

    Returns:
        The newly created UserModel.
    """
    try:
        db = get_database()
        user = UserModel(user_id=user_id)
        await db.users.insert_one(user.model_dump())
        logger.info("Created user %s", user_id)
        return user
    except Exception as exc:
        logger.error("create_user failed for %s: %s", user_id, exc)
        raise


async def get_user(user_id: str) -> Optional[UserModel]:
    """Fetch a user document by user_id.

    Returns:
        UserModel if the user exists, None otherwise.
    """
    try:
        db = get_database()
        doc = await db.users.find_one({"user_id": user_id})
        return UserModel(**doc) if doc else None
    except Exception as exc:
        logger.error("get_user failed for %s: %s", user_id, exc)
        raise


async def update_user_profile(
    user_id: str,
    prakriti: Optional[str] = None,
    dosha_scores: Optional[DoshaScores] = None,
    health_profile: Optional[HealthProfile] = None,
) -> bool:
    """Partially update a user's prakriti, dosha scores, or health profile.

    Only the fields that are not None will be written.

    Returns:
        True if a document was modified, False if the user was not found.
    """
    try:
        db = get_database()
        updates: dict = {}
        if prakriti is not None:
            updates["prakriti"] = prakriti
        if dosha_scores is not None:
            updates["dosha_scores"] = dosha_scores.model_dump()
        if health_profile is not None:
            updates["health_profile"] = health_profile.model_dump()

        if not updates:
            return False

        result = await db.users.update_one(
            {"user_id": user_id}, {"$set": updates}
        )
        return result.modified_count > 0
    except Exception as exc:
        logger.error("update_user_profile failed for %s: %s", user_id, exc)
        raise


# ── 2. sessions ───────────────────────────────────────────────────────────────

async def create_session(session_id: str, user_id: str) -> SessionModel:
    """Insert a new session document into the *sessions* collection.

    Args:
        session_id: UUID string for the session.
        user_id:    UUID string of the owning user.

    Returns:
        The newly created SessionModel.
    """
    try:
        db = get_database()
        session = SessionModel(session_id=session_id, user_id=user_id)
        await db.sessions.insert_one(session.model_dump())
        logger.info("Created session %s for user %s", session_id, user_id)
        return session
    except Exception as exc:
        logger.error("create_session failed (%s / %s): %s", session_id, user_id, exc)
        raise


async def get_session(session_id: str) -> Optional[SessionModel]:
    """Fetch a session document by session_id.

    Returns:
        SessionModel if found, None otherwise.
    """
    try:
        db = get_database()
        doc = await db.sessions.find_one({"session_id": session_id})
        return SessionModel(**doc) if doc else None
    except Exception as exc:
        logger.error("get_session failed for %s: %s", session_id, exc)
        raise


async def update_session(
    session_id: str,
    increment_message_count: bool = True,
    is_emergency: bool = False,
) -> bool:
    """Increment the message count and/or mark a session as an emergency.

    Returns:
        True if the document was modified, False if the session was not found.
    """
    try:
        db = get_database()
        update: dict = {}
        if increment_message_count:
            update["$inc"] = {"message_count": 1}
        if is_emergency:
            update.setdefault("$set", {})["is_emergency"] = True

        if not update:
            return False

        result = await db.sessions.update_one({"session_id": session_id}, update)
        return result.modified_count > 0
    except Exception as exc:
        logger.error("update_session failed for %s: %s", session_id, exc)
        raise


# ── 3. messages ───────────────────────────────────────────────────────────────

async def save_message(
    session_id: str,
    user_id: str,
    user_message: str,
    bot_response: str,
    sources: list[str],
    severity: str,
    is_emergency: bool,
) -> MessageModel:
    """Persist a chat exchange to the *messages* collection.

    Returns:
        The saved MessageModel (with auto-generated message_id and timestamp).
    """
    try:
        db = get_database()
        message = MessageModel(
            session_id=session_id,
            user_id=user_id,
            user_message=user_message,
            bot_response=bot_response,
            sources=sources,
            severity=severity,
            is_emergency=is_emergency,
        )
        await db.messages.insert_one(message.model_dump())
        logger.info("Saved message %s (session=%s)", message.message_id, session_id)
        return message
    except Exception as exc:
        logger.error("save_message failed: %s", exc)
        raise


async def get_session_messages(session_id: str) -> list[MessageModel]:
    """Retrieve all messages for a session, ordered by timestamp ascending.

    Returns:
        List of MessageModel objects (may be empty if session has no messages).
    """
    try:
        db = get_database()
        cursor = db.messages.find(
            {"session_id": session_id}, sort=[("timestamp", 1)]
        )
        docs = await cursor.to_list(length=None)
        return [MessageModel(**doc) for doc in docs]
    except Exception as exc:
        logger.error("get_session_messages failed for %s: %s", session_id, exc)
        raise


# ── 4. food_logs ──────────────────────────────────────────────────────────────

async def save_food_log(
    user_id: str,
    raw_text: str,
    meal_type: str = "snack",
    food_qualities: Optional[FoodQualities] = None,
) -> FoodLogModel:
    """Persist a food log entry for a user.

    Args:
        user_id:        The user logging the food.
        raw_text:       The original free-text description of the food.
        meal_type:      One of breakfast / lunch / dinner / snack.
        food_qualities: Optional Ayurvedic quality breakdown.

    Returns:
        The saved FoodLogModel (with auto-generated log_id and timestamp).
    """
    try:
        db = get_database()
        log = FoodLogModel(
            user_id=user_id,
            raw_text=raw_text,
            meal_type=meal_type,  # type: ignore[arg-type]
            food_qualities=food_qualities or FoodQualities(),
        )
        await db.food_logs.insert_one(log.model_dump())
        logger.info("Saved food log %s for user %s", log.log_id, user_id)
        return log
    except Exception as exc:
        logger.error("save_food_log failed for user %s: %s", user_id, exc)
        raise


async def get_recent_food_logs(user_id: str, days: int = 7) -> list[FoodLogModel]:
    """Retrieve food logs for a user from the last N days.

    Args:
        user_id: The user whose logs to fetch.
        days:    Look-back window in days (default 7).

    Returns:
        List of FoodLogModel objects ordered by timestamp descending.
    """
    try:
        db = get_database()
        since = _utcnow() - timedelta(days=days)
        cursor = db.food_logs.find(
            {"user_id": user_id, "timestamp": {"$gte": since}},
            sort=[("timestamp", -1)],
        )
        docs = await cursor.to_list(length=None)
        return [FoodLogModel(**doc) for doc in docs]
    except Exception as exc:
        logger.error("get_recent_food_logs failed for user %s: %s", user_id, exc)
        raise


async def get_recent_food_logs_hours(user_id: str, hours: int = 48) -> list[FoodLogModel]:
    """Retrieve food logs for a user from the last N hours.

    Args:
        user_id: The user whose logs to fetch.
        hours:   Look-back window in hours (default 48).

    Returns:
        List of FoodLogModel objects ordered by timestamp descending.
    """
    try:
        db = get_database()
        since = _utcnow() - timedelta(hours=hours)
        cursor = db.food_logs.find(
            {"user_id": user_id, "timestamp": {"$gte": since}},
            sort=[("timestamp", -1)],
        )
        docs = await cursor.to_list(length=None)
        return [FoodLogModel(**doc) for doc in docs]
    except Exception as exc:
        logger.error("get_recent_food_logs_hours failed for user %s: %s", user_id, exc)
        raise


async def get_food_logs_by_date(user_id: str, days: int = 7) -> list[FoodLogModel]:
    """Retrieve food logs for a user grouped by recent days.

    Alias for get_recent_food_logs for semantic clarity in route handlers.

    Args:
        user_id: The user whose logs to fetch.
        days:    Look-back window in days (default 7).

    Returns:
        List of FoodLogModel objects ordered by timestamp descending.
    """
    return await get_recent_food_logs(user_id, days=days)


async def get_today_food_logs(user_id: str) -> list[FoodLogModel]:
    """Retrieve today's food logs for a user.

    Args:
        user_id: The user whose logs to fetch.

    Returns:
        List of FoodLogModel objects from today, ordered by timestamp descending.
    """
    try:
        db = get_database()
        now = _utcnow()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        cursor = db.food_logs.find(
            {"user_id": user_id, "timestamp": {"$gte": start_of_day}},
            sort=[("timestamp", -1)],
        )
        docs = await cursor.to_list(length=None)
        return [FoodLogModel(**doc) for doc in docs]
    except Exception as exc:
        logger.error("get_today_food_logs failed for user %s: %s", user_id, exc)
        raise


async def delete_food_log(log_id: str) -> bool:
    """Delete a specific food log by log_id.

    Args:
        log_id: The log_id of the food log to delete.

    Returns:
        True if a document was deleted, False if not found.
    """
    try:
        db = get_database()
        result = await db.food_logs.delete_one({"log_id": log_id})
        if result.deleted_count > 0:
            logger.info("Deleted food log %s", log_id)
            return True
        return False
    except Exception as exc:
        logger.error("delete_food_log failed for %s: %s", log_id, exc)
        raise


# ── 5. feedback ───────────────────────────────────────────────────────────────

async def save_feedback(
    session_id: str,
    message_id: str,
    rating: str,
) -> FeedbackModel:
    """Persist user feedback on a bot message to the *feedback* collection.

    Args:
        session_id: The session the rated message belongs to.
        message_id: The specific message being rated.
        rating:     One of HELPFUL / NOT_HELPFUL / INACCURATE / EMERGENCY_MISSED.

    Returns:
        The saved FeedbackModel.
    """
    try:
        db = get_database()
        feedback = FeedbackModel(
            session_id=session_id,
            message_id=message_id,
            rating=rating,  # type: ignore[arg-type]
        )
        await db.feedback.insert_one(feedback.model_dump())
        logger.info(
            "Saved feedback %s for message %s (rating=%s)",
            feedback.feedback_id, message_id, rating,
        )
        return feedback
    except Exception as exc:
        logger.error("save_feedback failed: %s", exc)
        raise


# ── 6. user_profiles ──────────────────────────────────────────────────────────

async def create_user_profile(profile_data: dict) -> str:
    """Insert a new UserProfile document into the *user_profiles* collection.

    Args:
        profile_data: Dict matching the UserProfile schema.

    Returns:
        The user_id of the created profile.
    """
    try:
        db = get_database()
        profile = UserProfile(**profile_data)
        doc = profile.model_dump()
        await db.user_profiles.insert_one(doc)
        logger.info("Created user profile for %s", profile.user_id)
        return profile.user_id
    except Exception as exc:
        logger.error("create_user_profile failed: %s", exc)
        raise


async def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """Fetch a UserProfile document by user_id.

    Args:
        user_id: The user's ID.

    Returns:
        UserProfile if found, None otherwise.
    """
    try:
        db = get_database()
        doc = await db.user_profiles.find_one({"user_id": user_id})
        return UserProfile(**doc) if doc else None
    except Exception as exc:
        logger.error("get_user_profile failed for %s: %s", user_id, exc)
        raise


async def update_user_profile_fields(user_id: str, updates: dict) -> bool:
    """Partially update a UserProfile document with arbitrary field updates.

    Args:
        user_id: The user's ID.
        updates: Dict of fields to set (e.g. {"age": 26, "prakriti": "Vata"}).

    Returns:
        True if a document was modified, False if not found.
    """
    try:
        db = get_database()
        if not updates:
            return False
        result = await db.user_profiles.update_one(
            {"user_id": user_id}, {"$set": updates}
        )
        return result.modified_count > 0
    except Exception as exc:
        logger.error("update_user_profile_fields failed for %s: %s", user_id, exc)
        raise


async def update_dosha(
    user_id: str,
    prakriti: str,
    scores: dict,
    percentages: dict,
) -> bool:
    """Update the dosha assessment fields on an existing UserProfile.

    Args:
        user_id:     The user's ID.
        prakriti:    Dominant dosha label (e.g. "Pitta").
        scores:      Raw dosha scores {"vata": int, "pitta": int, "kapha": int}.
        percentages: Percentage breakdown {"vata": float, ...}.

    Returns:
        True if a document was modified, False if not found.
    """
    try:
        db = get_database()
        result = await db.user_profiles.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "prakriti": prakriti,
                    "dosha_scores": scores,
                    "dosha_percentages": percentages,
                    "onboarding_complete": True,
                }
            },
        )
        return result.modified_count > 0
    except Exception as exc:
        logger.error("update_dosha failed for %s: %s", user_id, exc)
        raise


async def check_user_exists(user_id: str) -> bool:
    """Check whether a UserProfile document exists for the given user_id.

    Args:
        user_id: The user's ID.

    Returns:
        True if the profile exists, False otherwise.
    """
    try:
        db = get_database()
        doc = await db.user_profiles.find_one({"user_id": user_id}, {"_id": 1})
        return doc is not None
    except Exception as exc:
        logger.error("check_user_exists failed for %s: %s", user_id, exc)
        raise
