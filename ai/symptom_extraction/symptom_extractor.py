"""
Symptom extraction module.
Uses spaCy to extract symptoms, triggers, duration, and body parts
from natural language user input.
"""

import spacy
import re
from typing import List, Dict

# Load spaCy model once at module level (expensive to reload each time)
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise OSError("spaCy model not found. Run: python -m spacy download en_core_web_sm")


# Known symptom vocabulary for matching
SYMPTOM_KEYWORDS = [
    "pain", "ache", "aching", "headache", "migraine", "fever", "cough",
    "nausea", "vomiting", "dizziness", "fatigue", "tiredness", "weakness",
    "shortness of breath", "chest pain", "back pain", "sore throat",
    "runny nose", "congestion", "rash", "swelling", "itching", "burning",
    "cramping", "bloating", "diarrhea", "constipation", "chills", "sweating",
    "insomnia", "anxiety", "palpitations", "blurred vision", "numbness",
    "tingling", "stiffness", "inflammation", "discharge", "bleeding",
]

# Trigger patterns (what caused or worsens the symptom)
TRIGGER_PATTERNS = [
    r'after (eating|drinking|exercise|running|sleeping|waking)',
    r'when (i eat|i drink|i exercise|i lie down|i stand)',
    r'due to (stress|anxiety|food|alcohol|caffeine)',
    r'caused by',
    r'because of',
    r'triggered by',
    r'(spicy|fatty|fried|dairy) food',
    r'(alcohol|caffeine|coffee)',
    r'(stress|anxiety|worry)',
    r'(screen|computer|phone) (time|use)',
]

# Duration patterns
DURATION_PATTERNS = [
    r'for (\d+) (hour|hours|day|days|week|weeks|month|months)',
    r'since (yesterday|last \w+|this morning)',
    r'(\d+) (hour|hours|day|days|week|weeks) ago',
    r'(a few|several) (hours|days|weeks)',
    r'all (day|night|week)',
    r'(past|last) (\d+) (hours|days|weeks)',
]

# Body part mentions
BODY_PARTS = [
    "head", "chest", "stomach", "abdomen", "back", "throat", "neck",
    "shoulder", "arm", "leg", "knee", "foot", "hand", "eye", "ear",
    "nose", "mouth", "jaw", "hip", "wrist", "ankle", "spine",
]


def extract_symptoms(text: str) -> List[str]:
    """
    Extract symptom mentions from text using keyword matching and spaCy.

    Args:
        text: User input string

    Returns:
        List of detected symptom strings
    """
    text_lower = text.lower()
    found_symptoms = []

    # Direct keyword matching
    for symptom in SYMPTOM_KEYWORDS:
        if symptom in text_lower:
            found_symptoms.append(symptom)

    # spaCy noun chunk extraction for symptoms not in our list
    doc = nlp(text)
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        # Look for pain/ache patterns in noun chunks
        if any(word in chunk_text for word in ["pain", "ache", "hurt", "sore"]):
            if chunk_text not in found_symptoms:
                found_symptoms.append(chunk_text)

    return list(set(found_symptoms))


def extract_triggers(text: str) -> List[str]:
    """
    Extract trigger/cause mentions from text.

    Args:
        text: User input string

    Returns:
        List of detected trigger strings
    """
    text_lower = text.lower()
    triggers = []

    for pattern in TRIGGER_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            triggers.append(match.group(0))

    return list(set(triggers))


def extract_duration(text: str) -> str:
    """
    Extract duration of symptoms from text.

    Args:
        text: User input string

    Returns:
        Duration string or empty string if not found
    """
    text_lower = text.lower()

    for pattern in DURATION_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            return match.group(0)

    return ""


def extract_body_parts(text: str) -> List[str]:
    """
    Extract mentioned body parts from text.

    Args:
        text: User input string

    Returns:
        List of mentioned body parts
    """
    text_lower = text.lower()
    found = []

    for part in BODY_PARTS:
        if re.search(rf'\b{part}\b', text_lower):
            found.append(part)

    return found


def extract_all(text: str) -> Dict:
    """
    Run all extractors on a user message and return structured result.

    Args:
        text: User input string

    Returns:
        Dictionary with symptoms, triggers, duration, body_parts
    """
    return {
        "symptoms":    extract_symptoms(text),
        "triggers":    extract_triggers(text),
        "duration":    extract_duration(text),
        "body_parts":  extract_body_parts(text),
    }