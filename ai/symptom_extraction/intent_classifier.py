"""
Intent classification module.
Detects what the user is trying to do from their message.
"""

import re
from enum import Enum


class Intent(Enum):
    SYMPTOM_ANALYSIS   = "SYMPTOM_ANALYSIS"    # describing symptoms
    EMERGENCY_CHECK    = "EMERGENCY_CHECK"      # possible emergency
    GENERAL_INFO       = "GENERAL_INFO"         # asking about a condition
    MEDICATION_QUERY   = "MEDICATION_QUERY"     # asking about medicine
    FOLLOWUP           = "FOLLOWUP"             # follow-up question
    GREETING           = "GREETING"             # hello/hi
    UNKNOWN            = "UNKNOWN"              # unclear


# Keyword patterns for each intent
INTENT_PATTERNS = {
    Intent.EMERGENCY_CHECK: [
        r'\bcan\'t breathe\b', r'\bchest pain\b', r'\bshortness of breath\b',
        r'\bunconscious\b', r'\blosing consciousness\b', r'\bsevere pain\b',
        r'\bcalling (911|999|112)\b', r'\bemergency\b', r'\bambulance\b',
        r'\bheart attack\b', r'\bstroke\b', r'\bnot breathing\b',
    ],
    Intent.MEDICATION_QUERY: [
        r'\bmedication\b', r'\bmedicine\b', r'\bdrug\b', r'\bpill\b',
        r'\bdosage\b', r'\bprescription\b', r'\bside effect\b',
        r'\bshould i take\b', r'\bcan i take\b',
    ],
    Intent.GENERAL_INFO: [
        r'\bwhat is\b', r'\bwhat are\b', r'\btell me about\b',
        r'\bhow does\b', r'\bexplain\b', r'\bdefine\b',
        r'\bwhat causes\b', r'\bwhy do(es)?\b',
    ],
    Intent.GREETING: [
        r'^(hi|hello|hey|howdy|good morning|good evening|good afternoon)[\s!?.]*$',
    ],
    Intent.SYMPTOM_ANALYSIS: [
        r'\bi have\b', r'\bi\'ve been\b', r'\bi feel\b', r'\bi am feeling\b',
        r'\bmy .* (hurts|aches|is|are)\b', r'\bsuffering from\b',
        r'\bexperiencing\b', r'\bsymptom\b', r'\bpain\b', r'\bache\b',
        r'\bnausea\b', r'\bdizziness\b', r'\bfever\b', r'\bcough\b',
        r'\btired\b', r'\bfatigue\b', r'\bheadache\b',
    ],
}


def classify_intent(text: str) -> dict:
    """
    Classify the intent of a user message.

    Checks emergency patterns first since they are highest priority.

    Args:
        text: User input string

    Returns:
        Dictionary with intent, confidence, and matched keywords
    """
    if not text or not isinstance(text, str):
        return {"intent": Intent.UNKNOWN.value, "confidence": 0.0, "matched": []}

    text_lower = text.lower().strip()
    scores = {}
    matched_keywords = {}

    # Check each intent's patterns
    for intent, patterns in INTENT_PATTERNS.items():
        matches = []
        for pattern in patterns:
            if re.search(pattern, text_lower):
                matches.append(pattern)
        if matches:
            scores[intent] = len(matches)
            matched_keywords[intent] = matches

    if not scores:
        return {"intent": Intent.UNKNOWN.value, "confidence": 0.0, "matched": []}

    # Emergency always wins if detected
    if Intent.EMERGENCY_CHECK in scores:
        return {
            "intent": Intent.EMERGENCY_CHECK.value,
            "confidence": 1.0,
            "matched": matched_keywords[Intent.EMERGENCY_CHECK]
        }

    # Pick the intent with the most pattern matches
    best_intent = max(scores, key=scores.get)
    total_patterns = len(INTENT_PATTERNS[best_intent])
    confidence = min(scores[best_intent] / total_patterns, 1.0)

    return {
        "intent": best_intent.value,
        "confidence": round(confidence, 2),
        "matched": matched_keywords[best_intent]
    }