"""
Context engine for Sevam — the brain of the system.

Builds unified context for the LLM by combining:
1. User profile (prakriti, health conditions)
2. Recent food logs (last 48h)
3. Food-symptom correlation analysis
4. Enriched RAG retrieval query

This context is passed to the LLM to generate personalized Ayurvedic responses.
"""

import logging
from typing import Optional

from backend.services.db_service import (
    get_user,
    get_recent_food_logs_hours,
    get_user_profile,
)
from backend.services.food_analyzer import FoodAnalyzer
from backend.services.correlation_engine import CorrelationEngine

logger = logging.getLogger(__name__)

_food_analyzer = FoodAnalyzer()
_correlation_engine = CorrelationEngine()


class ContextEngine:
    """
    Builds unified context for the LLM by merging user profile,
    food history, and symptom correlations.
    """

    def __init__(self):
        """Initialize with shared analyzer and correlation engine instances."""
        self.food_analyzer = _food_analyzer
        self.correlation_engine = _correlation_engine

    async def build_context(self, user_id: str, symptom: str) -> dict:
        """
        Build enriched context for LLM response generation.

        Steps:
        1. Load full UserProfile from user_profiles collection (prakriti,
           dosha_scores, health_profile including conditions and allergies)
        2. Fall back to legacy users collection if no onboarding profile found
        3. Load last 48h food logs from MongoDB
        4. Run food-symptom correlation
        5. Build enriched RAG retrieval query (includes prakriti)
        6. Return unified context dict

        Args:
            user_id: The user's ID
            symptom: The reported symptom or health query

        Returns:
            Unified context dict with user profile, food correlation,
            retrieval query, system prefix, and food summary.
        """
        # 1. Load full onboarding profile (Phase 8D)
        prakriti = "Unknown"
        health_profile: dict = {}
        conditions: list[str] = []
        allergies: list[str] = []
        dosha_scores: dict = {}
        user_name = ""

        try:
            full_profile = await get_user_profile(user_id)
            if full_profile:
                prakriti = full_profile.prakriti
                dosha_scores = full_profile.dosha_scores
                user_name = full_profile.name or ""
                if full_profile.health_profile:
                    hp = full_profile.health_profile
                    health_profile = hp.model_dump()
                    conditions = hp.conditions or []
                    allergies = hp.allergies or []
            else:
                # 2. Fallback: legacy users collection
                user = await get_user(user_id)
                if user:
                    prakriti = user.prakriti
                    health_profile = user.health_profile.model_dump() if user.health_profile else {}
                    conditions = health_profile.get("conditions", [])
                    allergies = health_profile.get("allergies", [])
        except Exception as exc:
            logger.warning("Could not load profile for %s: %s", user_id, exc)

        # 2. Load last 48h food logs
        food_logs_raw = []
        try:
            food_log_models = await get_recent_food_logs_hours(user_id, hours=48)
            food_logs_raw = [
                {
                    "raw_text": log.raw_text,
                    "meal_type": log.meal_type,
                    "timestamp": log.timestamp,
                    "qualities": log.food_qualities.model_dump() if log.food_qualities else {},
                }
                for log in food_log_models
            ]
        except Exception as exc:
            logger.warning("Could not load food logs for %s: %s", user_id, exc)

        # 3. Run food-symptom correlation
        correlation = self.correlation_engine.analyze_correlation(symptom, food_logs_raw)

        # 4. Build enriched retrieval query (prakriti-aware)
        retrieval_query = self._build_retrieval_query(
            symptom, prakriti, correlation, conditions
        )

        # 5. Build system prefix for LLM (full profile context)
        system_prefix = self._build_system_prefix(
            prakriti, symptom, correlation, food_logs_raw,
            conditions=conditions, allergies=allergies,
            dosha_scores=dosha_scores, user_name=user_name,
        )

        # 6. Build food summary
        food_summary = self._summarize_food_logs(food_logs_raw)

        return {
            "user_id": user_id,
            "prakriti": prakriti,
            "dosha_scores": dosha_scores,
            "symptom": symptom,
            "conditions": conditions,
            "allergies": allergies,
            "food_correlation": {
                "has_correlation": correlation["has_correlation"],
                "likely_trigger": correlation.get("likely_trigger"),
                "dosha_aggravated": correlation.get("dosha_aggravated"),
                "correlation_strength": correlation.get("correlation_strength"),
                "explanation": correlation.get("explanation", ""),
                "dietary_advice": correlation.get("dietary_advice", ""),
            },
            "retrieval_query": retrieval_query,
            "system_prefix": system_prefix,
            "recent_food_summary": food_summary,
        }

    def _build_retrieval_query(
        self,
        symptom: str,
        prakriti: str,
        correlation: dict,
        conditions: list[str] | None = None,
    ) -> str:
        """
        Build an enriched query for RAG retrieval.

        Adds dosha, correlation, and health-condition context to the raw
        symptom query so the vector search returns more relevant results.

        Args:
            symptom: Raw symptom text
            prakriti: User's prakriti type
            correlation: Correlation analysis result
            conditions: Known health conditions (e.g. ["diabetes"])

        Returns:
            Enriched query string for vector search
        """
        parts = [symptom]

        if prakriti and prakriti != "Unknown":
            dominant = prakriti.split("-")[0]
            parts.append(f"{dominant} dosha")

        if conditions:
            parts.extend(conditions)

        if correlation.get("has_correlation"):
            dosha = correlation.get("dosha_aggravated", "")
            if dosha:
                parts.append(f"{dosha} aggravation")
            if correlation.get("likely_trigger"):
                parts.append("food correlation")

        return " ".join(parts)

    def _build_system_prefix(
        self,
        prakriti: str,
        symptom: str,
        correlation: dict,
        food_logs: list[dict],
        conditions: list[str] | None = None,
        allergies: list[str] | None = None,
        dosha_scores: dict | None = None,
        user_name: str = "",
    ) -> str:
        """
        Build a system instruction prefix for the LLM.

        Includes the user's full prakriti, health conditions, allergies,
        recent food history, and any food-symptom correlations found.

        Args:
            prakriti: User's dosha type (e.g. "Pitta" or "Pitta-Vata")
            symptom: Reported symptom
            correlation: Correlation result
            food_logs: Recent food log dicts
            conditions: Known medical conditions
            allergies: Known food allergies
            dosha_scores: Raw dosha score dict
            user_name: User's name (optional, for personalisation)

        Returns:
            System prefix string for LLM context
        """
        lines = []

        # Identity
        greeting = f"User {user_name} is" if user_name else "User is"
        if prakriti and prakriti != "Unknown":
            lines.append(f"{greeting} {prakriti} dominant (Ayurvedic constitution).")
            if dosha_scores:
                score_str = ", ".join(
                    f"{d.capitalize()}: {s}"
                    for d, s in dosha_scores.items()
                    if isinstance(s, (int, float))
                )
                if score_str:
                    lines.append(f"Dosha scores — {score_str}.")
        else:
            lines.append(f"{greeting} yet to determine their prakriti.")

        # Health conditions — mention explicitly so LLM tailors advice
        if conditions:
            cond_str = ", ".join(conditions)
            lines.append(
                f"Known health conditions: {cond_str}. "
                "Tailor recommendations to be safe for these conditions."
            )

        # Allergies — instruct LLM to exclude
        if allergies:
            allergy_str = ", ".join(allergies)
            lines.append(
                f"Known allergies: {allergy_str}. "
                "Do NOT recommend these herbs, foods, or substances."
            )

        # Recent meals
        if food_logs:
            recent_foods = [log["raw_text"] for log in food_logs[:5]]
            lines.append(f"Recent meals (last 48h): {', '.join(recent_foods)}.")

        # Food-symptom correlation
        if correlation.get("has_correlation"):
            trigger = correlation.get("likely_trigger", "")
            dosha = correlation.get("dosha_aggravated", "")
            lines.append(
                f"Food-symptom correlation detected: {trigger} likely aggravated {dosha} dosha."
            )
            lines.append("Factor this dietary context into your advice.")
        else:
            lines.append("No clear food-symptom correlation found in recent meals.")

        lines.append(
            "Provide personalised Ayurvedic advice considering the user's "
            "constitution, health history, and recent diet."
        )

        return " ".join(lines)

    def _summarize_food_logs(self, food_logs: list[dict]) -> str:
        """
        Create a brief human-readable summary of recent food logs.

        Args:
            food_logs: List of food log dicts

        Returns:
            Summary string like "Last 48h: biryani (heavy/spicy), idli (light)"
        """
        if not food_logs:
            return "No food logs in last 48 hours."

        items = []
        for log in food_logs[:10]:
            food = log.get("raw_text", "unknown")
            qualities = log.get("qualities", {})
            q_parts = []
            hl = qualities.get("heavy_light")
            sb = qualities.get("spicy_bland")
            if hl and hl != "light":
                q_parts.append(hl)
            if sb and sb != "bland":
                q_parts.append(sb)

            if q_parts:
                items.append(f"{food} ({'/'.join(q_parts)})")
            else:
                items.append(food)

        return f"Last 48h: {', '.join(items)}"
