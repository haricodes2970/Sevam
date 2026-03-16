"""
Medic Night chatbot — main conversational engine.
Combines NLP analysis, RAG retrieval, safety checks, and LLM generation.

This is the brain of the entire system.
"""

from typing import Dict

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.symptom_extraction.analyzer import analyze
from backend.rag_pipeline.retriever import MedicalRetriever
from backend.services.llm_client import HuggingFaceLLM
from backend.services.safety_guard import (
    is_emergency, apply_safety_wrapper,
    check_response_safety, sanitize_input
)
from backend.services.prompt_builder import build_rag_prompt, build_general_prompt


class MedicNightChatbot:
    """
    Main chatbot class for Medic Night.
    Orchestrates the full pipeline for every user message.
    """

    def __init__(self):
        """Initialize all components."""
        print("🩺 Initializing Medic Night Chatbot...\n")
        self.retriever   = MedicalRetriever()
        self.llm         = HuggingFaceLLM()
        self.history     = []  # Conversation memory
        print("\n✅ Chatbot ready!\n")

    def chat(self, user_message: str) -> Dict:
        """
        Process a user message through the full pipeline.

        Pipeline:
        1. Sanitize input
        2. Check for emergency
        3. Analyze with NLP
        4. Retrieve relevant chunks
        5. Build grounded prompt
        6. Generate LLM response
        7. Apply safety wrapper
        8. Update conversation history

        Args:
            user_message: Raw user input string

        Returns:
            Dict with response, metadata, and retrieved context
        """
        # Step 1 — Sanitize
        clean_message = sanitize_input(user_message)

        # Step 2 — Emergency check (always first)
        emergency_detected = is_emergency(clean_message)
        if emergency_detected:
            from backend.services.safety_guard import EMERGENCY_RESPONSE
            self._add_to_history(user_message, EMERGENCY_RESPONSE)
            return {
                "response": EMERGENCY_RESPONSE,
                "intent": "EMERGENCY_CHECK",
                "severity": "EMERGENCY",
                "is_emergency": True,
                "retrieved_chunks": [],
                "sources": []
            }

        # Step 3 — NLP analysis
        analysis = analyze(clean_message)

        # Step 4 — Retrieve relevant chunks
        retrieved = self.retriever.retrieve_with_emergency_boost(
            query=clean_message,
            is_emergency=analysis.get("is_emergency", False)
        )

        # Step 5 — Build prompt based on intent
        intent = analysis.get("intent", "UNKNOWN")
        if intent in ["SYMPTOM_ANALYSIS", "GENERAL_INFO", "UNKNOWN"]:
            prompt = build_rag_prompt(
                user_message=clean_message,
                retrieved_chunks=retrieved,
                conversation_history=self.history
            )
        else:
            prompt = build_general_prompt(clean_message)

        # Step 6 — Generate LLM response
        raw_response = self.llm.generate(prompt)

        # Step 7 — Safety check and wrap
        safety_check = check_response_safety(raw_response)
        final_response = apply_safety_wrapper(
            raw_response,
            is_emergency_case=False
        )

        # Step 8 — Update history
        self._add_to_history(user_message, final_response)

        return {
            "response":        final_response,
            "intent":          intent,
            "severity":        analysis.get("severity"),
            "symptoms":        analysis.get("symptoms", []),
            "is_emergency":    False,
            "safety_passed":   safety_check["is_safe"],
            "retrieved_chunks": len(retrieved),
            "sources": [r["title"] for r in retrieved if r.get("similarity", 0) > 0]
        }

    def _add_to_history(self, user_msg: str, assistant_msg: str) -> None:
        """Add a turn to conversation history."""
        self.history.append({"role": "user",      "content": user_msg})
        self.history.append({"role": "assistant",  "content": assistant_msg})

        # Keep only last 10 turns to avoid context overflow
        if len(self.history) > 10:
            self.history = self.history[-10:]

    def reset(self) -> None:
        """Clear conversation history."""
        self.history = []
        print("Conversation reset.")


if __name__ == "__main__":
    print("="*55)
    print("   🩺 Medic Night — Chatbot Test")
    print("="*55)

    bot = MedicNightChatbot()

    test_messages = [
        "I have a bad headache for 3 days",
        "Could it be related to stress?",
        "I also feel dizzy sometimes",
        "My chest hurts and I can't breathe",
    ]

    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        result = bot.chat(msg)
        print(f"\n🤖 Medic Night:\n{result['response']}")
        print(f"\n   [Intent: {result['intent']} | Severity: {result['severity']} | Sources: {result['sources']}]")
        print("-"*55)
