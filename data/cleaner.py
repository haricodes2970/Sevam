"""
Medical text cleaning module.
Cleans and normalizes raw medical text for RAG processing.
"""

import re
import string


def clean_text(text: str) -> str:
    """
    Clean and normalize medical text.
    
    Args:
        text: Raw medical text string
        
    Returns:
        Cleaned and normalized text string
    """
    if not text or not isinstance(text, str):
        return ""

    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)

    # Remove special characters but keep medical punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\/\%\°]', '', text)

    # Fix spacing around punctuation
    text = re.sub(r'\s([?.!,;:])', r'\1', text)

    # Remove multiple consecutive punctuation
    text = re.sub(r'([.!?]){2,}', r'\1', text)

    # Normalize to single spaces
    text = ' '.join(text.split())

    return text.strip()


def normalize_medical_terms(text: str) -> str:
    """
    Normalize common medical abbreviations and terms.
    
    Args:
        text: Cleaned medical text
        
    Returns:
        Text with normalized medical terms
    """
    replacements = {
        r'\bGERD\b': 'gastroesophageal reflux disease (GERD)',
        r'\bBP\b': 'blood pressure (BP)',
        r'\bHR\b': 'heart rate (HR)',
        r'\bECG\b': 'electrocardiogram (ECG)',
        r'\bCT\b': 'computed tomography (CT)',
        r'\bMRI\b': 'magnetic resonance imaging (MRI)',
        r'\bUTI\b': 'urinary tract infection (UTI)',
        r'\bOTC\b': 'over-the-counter (OTC)',
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    return text


def clean_document(doc: dict) -> dict:
    """
    Clean a full medical document dictionary.
    
    Args:
        doc: Raw document with id, title, source, content fields
        
    Returns:
        Cleaned document dictionary
    """
    cleaned = doc.copy()

    if 'content' in cleaned:
        cleaned['content'] = clean_text(cleaned['content'])
        cleaned['content'] = normalize_medical_terms(cleaned['content'])

    if 'title' in cleaned:
        cleaned['title'] = clean_text(cleaned['title'])

    # Add metadata
    cleaned['word_count'] = len(cleaned.get('content', '').split())
    cleaned['is_emergency'] = cleaned.get('source') == 'emergency'

    return cleaned