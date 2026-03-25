"""
Main NLP symptom analyzer.
Combines intent, symptom extraction, and severity into one result.

Run: python ai/symptom_extraction/analyzer.py
"""

import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from ai.symptom_extraction.intent_classifier import classify_intent
from ai.symptom_extraction.symptom_extractor import extract_all
from ai.symptom_extraction.severity_detector import detect_severity


def analyze(user_message: str) -> dict:
    """
    Run full NLP analysis on a user message.

    Args:
        user_message: Raw text from the user

    Returns:
        Structured analysis dictionary with all extracted fields
    """
    if not user_message or not user_message.strip():
        return {"error": "Empty message received"}

    # Run all three analyzers
    intent_result   = classify_intent(user_message)
    extracted       = extract_all(user_message)
    severity_result = detect_severity(user_message, extracted["symptoms"])

    return {
        "original_message": user_message,
        "intent":           intent_result["intent"],
        "intent_confidence": intent_result["confidence"],
        "symptoms":         extracted["symptoms"],
        "triggers":         extracted["triggers"],
        "duration":         extracted["duration"],
        "body_parts":       extracted["body_parts"],
        "severity":         severity_result["severity"],
        "severity_score":   severity_result["score"],
        "severity_indicators": severity_result["indicators"],
        "is_emergency":     severity_result["severity"] == "EMERGENCY",
    }


def print_analysis(result: dict) -> None:
    """Pretty print the analysis result."""
    print("\n" + "="*55)
    print(f"  Message  : {result.get('original_message', '')}")
    print("="*55)
    print(f"  Intent   : {result.get('intent')} (confidence: {result.get('intent_confidence')})")
    print(f"  Symptoms : {result.get('symptoms')}")
    print(f"  Triggers : {result.get('triggers')}")
    print(f"  Duration : {result.get('duration') or 'not mentioned'}")
    print(f"  Body     : {result.get('body_parts')}")
    print(f"  Severity : {result.get('severity')} (score: {result.get('severity_score')})")
    print(f"  Emergency: {result.get('is_emergency')}")
    print("="*55)


if __name__ == "__main__":
    print("🧠 Sevam — NLP Symptom Analyzer\n")

    test_messages = [
        "I have a bad headache for 3 days and feel nauseous",
        "My chest hurts and I can't breathe properly",
        "I feel a slight sore throat after drinking cold water",
        "I've been having severe back pain for the past week",
        "What is tonsillitis?",
        "I have fever, chills, and a cough since yesterday",
    ]

    for msg in test_messages:
        result = analyze(msg)
        print_analysis(result)

    print("\n✅ NLP analyzer working! Ready for Phase 3.\n")
