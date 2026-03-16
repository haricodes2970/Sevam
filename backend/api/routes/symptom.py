from fastapi import APIRouter, HTTPException
from backend.models.schemas import (
    SymptomAnalysisRequest, SymptomAnalysisResponse,
    SeverityLevel, IntentType
)

router = APIRouter()


@router.post("/analyze-symptom", response_model=SymptomAnalysisResponse, tags=["Analysis"])
async def analyze_symptom(request: SymptomAnalysisRequest) -> SymptomAnalysisResponse:
    try:
        from ai.symptom_extraction.analyzer import SymptomAnalyzer
        analyzer = SymptomAnalyzer()
        result = analyzer.analyze(request.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"NLP analysis failed: {str(e)}")

    return SymptomAnalysisResponse(
        original_message=result["original_message"],
        intent=IntentType(result["intent"]),
        intent_confidence=result.get("intent_confidence", 0.0),
        symptoms=result.get("symptoms", []),
        triggers=result.get("triggers", []),
        duration=result.get("duration"),
        body_parts=result.get("body_parts", []),
        severity=SeverityLevel(result["severity"]),
        severity_score=result.get("severity_score", 1),
        severity_indicators=result.get("severity_indicators", []),
        is_emergency=result.get("is_emergency", False),
    )