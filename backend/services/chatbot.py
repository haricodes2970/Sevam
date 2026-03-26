"""
Sevam chatbot — async conversational engine.

Full pipeline per message:
  1. Sanitize input
  2. Safety guard (emergency check)
  3. Context engine → user profile + food logs + correlation
  4. RAG retriever → Ayurvedic knowledge chunks
  5. Prompt builder → (system_msg, user_msg) for Ollama
  6. Ollama LLM → generate response
  7. Safety wrapper → add disclaimer
  8. Return enriched result dict
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from backend.rag_pipeline.retriever import MedicalRetriever
from backend.services.llm_client import generate_chat
from backend.services.safety_guard import (
    is_emergency,
    apply_safety_wrapper,
    check_response_safety,
    sanitize_input,
    EMERGENCY_RESPONSE,
)
from backend.services.prompt_builder import build_ayurvedic_prompt
from backend.services.context_engine import ContextEngine

logger = logging.getLogger(__name__)


class SevamChatbot:
    """
    Async chatbot that orchestrates the full Sevam pipeline.

    Heavy components (retriever, LLM) are initialised once in __init__.
    The context engine is lightweight and created fresh per instance.
    Conversation history is kept per chatbot instance (in-process memory).
    """

    def __init__(self) -> None:
        """Initialise retriever, LLM, and context engine."""
        logger.info("Initialising Sevam Chatbot...")
        self.retriever = MedicalRetriever()
        self.context_engine = ContextEngine()
        self._history: List[Dict] = []   # simple in-process conversation memory
        logger.info("Sevam Chatbot ready.")

    # ── Public API ────────────────────────────────────────────────────────────

    async def chat(
        self,
        user_id: str,
        message: str,
        session_id: Optional[str] = None,
    ) -> Dict:
        """
        Process one user message through the full pipeline.

        Pipeline:
        1. Sanitize + emergency check
        2. Build context (user profile, food logs, correlation)
        3. Retrieve Ayurvedic knowledge chunks (using enriched query)
        4. Build Groq-format prompt
        5. Generate LLM response
        6. Apply safety wrapper
        7. Update conversation history
        8. Return enriched result

        Args:
            user_id:    User's identifier (used to load profile + food logs)
            message:    Raw user message
            session_id: Optional session identifier (for logging only)

        Returns:
            Dict with keys: response, sources, severity, is_emergency,
            food_correlation, prakriti, dosha_scores
        """
        # Step 1 — Sanitize
        clean_message = sanitize_input(message)

        # Step 2 — Emergency check (always first, no DB needed)
        if is_emergency(clean_message):
            logger.warning("Emergency detected for user %s: %s", user_id, clean_message[:60])
            self._add_to_history(message, EMERGENCY_RESPONSE)
            return {
                "response": EMERGENCY_RESPONSE,
                "severity": "EMERGENCY",
                "is_emergency": True,
                "sources": [],
                "food_correlation": {"has_correlation": False},
                "prakriti": "Unknown",
                "dosha_scores": {},
            }

        # Step 3 — Build context (user profile + food logs + correlation)
        context = await self._load_context(user_id, clean_message)

        # Step 4 — RAG retrieval using enriched query
        retrieval_query = context.get("retrieval_query", clean_message)
        retrieved_chunks = self._retrieve(retrieval_query)

        # Step 5 — Build prompt
        system_msg, user_msg = build_ayurvedic_prompt(
            user_message=clean_message,
            system_prefix=context.get("system_prefix", ""),
            retrieved_chunks=retrieved_chunks,
            food_correlation=context.get("food_correlation"),
            conversation_history=self._history,
        )

        # Step 6 — Generate
        raw_response = self._generate(system_msg, user_msg)

        # Step 7 — Safety wrapper
        check_response_safety(raw_response)   # logs issues but doesn't block
        final_response = apply_safety_wrapper(raw_response, is_emergency_case=False)

        # Step 8 — Update history
        self._add_to_history(message, final_response)

        # Build source list from retrieved chunks
        sources = [
            r["title"]
            for r in retrieved_chunks
            if r.get("similarity", 0) > 0 and r.get("title")
        ]

        return {
            "response": final_response,
            "severity": self._infer_severity(context),
            "is_emergency": False,
            "sources": sources,
            "food_correlation": context.get("food_correlation", {"has_correlation": False}),
            "prakriti": context.get("prakriti", "Unknown"),
            "dosha_scores": context.get("dosha_scores", {}),
        }

    def reset(self) -> None:
        """Clear in-process conversation history."""
        self._history = []
        logger.info("Conversation history reset.")

    # ── Private helpers ───────────────────────────────────────────────────────

    async def _load_context(self, user_id: str, message: str) -> Dict:
        """
        Load enriched context from the ContextEngine.

        Falls back to a minimal context dict on failure so the chat never
        crashes due to a DB or network issue.

        Args:
            user_id: User identifier
            message: Current user message (used as symptom for correlation)

        Returns:
            Context dict from ContextEngine.build_context()
        """
        try:
            return await self.context_engine.build_context(user_id, message)
        except Exception as exc:
            logger.warning("Context engine failed for %s: %s", user_id, exc)
            return {
                "prakriti": "Unknown",
                "dosha_scores": {},
                "conditions": [],
                "allergies": [],
                "retrieval_query": message,
                "system_prefix": "User's profile could not be loaded.",
                "food_correlation": {"has_correlation": False},
                "recent_food_summary": "",
            }

    def _retrieve(self, query: str, n_results: int = 4) -> List[Dict]:
        """
        Retrieve Ayurvedic knowledge chunks for the given query.

        Returns an empty list rather than raising on failure.

        Args:
            query:     Enriched query string from ContextEngine
            n_results: Number of chunks to retrieve

        Returns:
            List of chunk dicts (may be empty)
        """
        try:
            return self.retriever.retrieve(query, n_results=n_results)
        except Exception as exc:
            logger.warning("RAG retrieval failed for query '%s': %s", query[:60], exc)
            return []

    def _generate(self, system_message: str, user_message: str) -> str:
        """
        Call the LLM to generate a response.

        Args:
            system_message: Ollama system role content
            user_message:   Ollama user role content

        Returns:
            Generated text string
        """
        return generate_chat(
            system_message=system_message,
            user_message=user_message,
        )

    def _infer_severity(self, context: Dict) -> str:
        """
        Infer severity from context (food correlation strength, conditions).

        Returns "HIGH", "MEDIUM", or "LOW".

        Args:
            context: Context dict from ContextEngine

        Returns:
            Severity string
        """
        corr = context.get("food_correlation", {})
        strength = corr.get("correlation_strength", "")
        if strength == "HIGH":
            return "HIGH"
        if strength == "MEDIUM" or corr.get("has_correlation"):
            return "MEDIUM"
        conditions = context.get("conditions", [])
        if conditions:
            return "MEDIUM"
        return "LOW"

    def _add_to_history(self, user_msg: str, assistant_msg: str) -> None:
        """
        Append a turn to in-process conversation history.

        Keeps only the last 10 turns to avoid context overflow.

        Args:
            user_msg:      The user's original message
            assistant_msg: The assistant's response
        """
        self._history.append({"role": "user",      "content": user_msg})
        self._history.append({"role": "assistant",  "content": assistant_msg})
        if len(self._history) > 10:
            self._history = self._history[-10:]
