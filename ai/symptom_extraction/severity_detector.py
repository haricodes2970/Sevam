"""
Severity detection module.
Determines how serious a user's described symptoms are.
"""

import re
from enum import Enum
from typing import Dict, List


class Severity(Enum):
    LOW      = "LOW"       # mild, manageable at home
    MEDIUM   = "MEDIUM"    # warrants monitoring or GP visit
    HIGH     = "HIGH"      # needs prompt medical attention
    EMERGENCY = "EMERGENCY" # call emergency services now


# Words that indicate severity level
SEVERITY_INDICATORS = {
    Severity.EMERGENCY: [
        "can't breathe", "cannot breathe", "not breathing",
        "chest pain", "heart attack", "stroke", "unconscious",
        "severe chest", "crushing pain", "loss of consciousness",
        "uncontrolled bleeding", "difficulty breathing",
        "worst headache", "sudden severe",
    ],
    Severity.HIGH: [
        "severe", "unbearable", "excruciating", "very bad",
        "extremely", "worst", "high fever", "can't move",
        "cannot move", "getting worse", "spreading",
        "vomiting blood", "blood in", "can't eat", "can't drink",
    ],
    Severity.MEDIUM: [
        "moderate", "persistent", "recurring", "keeps coming back",
        "for days", "for weeks", "not getting better",
        "affecting", "disrupting", "waking me up",
        "quite bad", "pretty bad", "uncomfortable",
    ],
    Severity.LOW: [
        "mild", "slight", "a little", "a bit", "minor",
        "not too bad", "manageable", "started recently",
        "just started", "comes and goes", "occasionally",
    ],
}


def detect_severity(text: str, symptoms: List[str] = None) -> Dict:
    """
    Detect the severity level of described symptoms.

    Checks emergency indicators first, then works down.
    Also considers number of symptoms as a factor.

    Args:
        text: User input string
        symptoms: Optional list of already extracted symptoms

    Returns:
        Dictionary with severity level, score, and matched indicators
    """
    if not text:
        return {"severity": Severity.LOW.value, "score": 0, "indicators": []}

    text_lower = text.lower()
    matched = {}

    for level, indicators in SEVERITY_INDICATORS.items():
        hits = [ind for ind in indicators if ind in text_lower]
        if hits:
            matched[level] = hits

    # Emergency is always highest priority
    if Severity.EMERGENCY in matched:
        return {
            "severity": Severity.EMERGENCY.value,
            "score": 10,
            "indicators": matched[Severity.EMERGENCY]
        }

    if Severity.HIGH in matched:
        return {
            "severity": Severity.HIGH.value,
            "score": 7,
            "indicators": matched[Severity.HIGH]
        }

    # Bump up to MEDIUM if many symptoms even with LOW words
    if symptoms and len(symptoms) >= 3 and Severity.MEDIUM not in matched:
        return {
            "severity": Severity.MEDIUM.value,
            "score": 4,
            "indicators": ["multiple symptoms detected"]
        }

    if Severity.MEDIUM in matched:
        return {
            "severity": Severity.MEDIUM.value,
            "score": 4,
            "indicators": matched[Severity.MEDIUM]
        }

    return {
        "severity": Severity.LOW.value,
        "score": 1,
        "indicators": matched.get(Severity.LOW, ["no high severity indicators found"])
    }