"""
Safety guardrail module.
Ensures all medical responses are safe, grounded, and responsible.
Detects emergencies and adds appropriate warnings.
"""

import re
from typing import Dict


# Emergency symptom patterns — any of these trigger immediate escalation
EMERGENCY_PATTERNS = [
    r"can'?t breathe", r"cannot breathe", r"not breathing",
    r"chest pain", r"crushing (chest|pain)",
    r"heart attack", r"stroke",
    r"loss of consciousness", r"unconscious", r"passed out",
    r"severe (chest|abdominal) pain",
    r"difficulty breathing", r"shortness of breath",
    r"uncontrolled bleeding", r"vomiting blood",
    r"worst headache", r"sudden (severe|numbness|weakness)",
    r"face (drooping|droop)", r"arm (weakness|numb)",
    r"slurred speech", r"vision (loss|sudden)",
]

EMERGENCY_RESPONSE = """
⚠️ MEDICAL EMERGENCY DETECTED

Your symptoms may indicate a serious medical emergency.

**Please take immediate action:**
- Call emergency services (911 / 999 / 112) immediately
- Do not drive yourself to the hospital
- Stay on the line with emergency services

This is not the time for online research. Please seek help now.
""".strip()

DISCLAIMER = "\n\n---\n*This information is for general guidance only. Always consult a qualified healthcare professional for medical advice, diagnosis, or treatment.*"


def is_emergency(text: str) -> bool:
    """
    Check if user message contains emergency symptoms.

    Args:
        text: User input string

    Returns:
        True if emergency patterns detected
    """
    text_lower = text.lower()
    for pattern in EMERGENCY_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def check_response_safety(response: str) -> Dict:
    """
    Validate that an LLM response meets safety standards.
    Checks that the response doesn't make definitive diagnoses
    or recommend specific medications/dosages.

    Args:
        response: Raw LLM response string

    Returns:
        Dict with is_safe bool and list of issues found
    """
    issues = []
    response_lower = response.lower()

    # Flag definitive diagnosis language
    diagnosis_patterns = [
        r"you (definitely|certainly|have|are diagnosed with)",
        r"you (must|should) (take|use) \w+mg",
        r"take (\d+)mg of",
        r"you are suffering from",
    ]
    for pattern in diagnosis_patterns:
        if re.search(pattern, response_lower):
            issues.append(f"Definitive diagnosis language detected: {pattern}")

    return {
        "is_safe": len(issues) == 0,
        "issues": issues
    }


def apply_safety_wrapper(response: str, is_emergency_case: bool = False) -> str:
    """
    Apply safety disclaimer and emergency header if needed.

    Args:
        response: LLM generated response
        is_emergency_case: Whether this was flagged as emergency

    Returns:
        Safety-wrapped response string
    """
    if is_emergency_case:
        return EMERGENCY_RESPONSE

    # Add disclaimer to all medical responses
    return response + DISCLAIMER


def sanitize_input(text: str) -> str:
    """
    Clean user input before sending to LLM.
    Removes potential prompt injection attempts.

    Args:
        text: Raw user input

    Returns:
        Sanitized input string
    """
    if not text:
        return ""

    # Remove any attempts to override system prompt
    injection_patterns = [
        r"ignore (previous|all|above) instructions",
        r"system prompt",
        r"you are now",
        r"forget (everything|all)",
        r"new instructions",
    ]

    text_lower = text.lower()
    for pattern in injection_patterns:
        if re.search(pattern, text_lower):
            return "I have a question about my symptoms."

    # Limit length to prevent abuse
    return text[:1000].strip()