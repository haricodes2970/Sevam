import json
from pathlib import Path
from fastapi import APIRouter
from backend.models.schemas import HealthResponse, ServiceStatus

router = APIRouter()

PROCESSED_CHUNKS_PATH = Path("data/processed/processed_chunks.json")
VECTOR_DB_PATH = Path("data/vector_db")


def _check_data_layer() -> ServiceStatus:
    try:
        if not PROCESSED_CHUNKS_PATH.exists():
            return ServiceStatus(status="down", detail="processed_chunks.json not found")
        with open(PROCESSED_CHUNKS_PATH) as f:
            chunks = json.load(f)
        return ServiceStatus(status="ok", detail=f"{len(chunks)} chunks loaded")
    except Exception as e:
        return ServiceStatus(status="down", detail=str(e))


def _check_vector_db() -> ServiceStatus:
    try:
        if not VECTOR_DB_PATH.exists():
            return ServiceStatus(status="down", detail="Vector DB not found — run indexer.py first")
        return ServiceStatus(status="ok")
    except Exception as e:
        return ServiceStatus(status="down", detail=str(e))


def _check_nlp() -> ServiceStatus:
    try:
        import spacy
        spacy.load("en_core_web_sm")
        return ServiceStatus(status="ok")
    except Exception as e:
        return ServiceStatus(status="down", detail=str(e))


@router.get("/health-check", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    services = {
        "data_layer": _check_data_layer(),
        "vector_db": _check_vector_db(),
        "nlp": _check_nlp(),
    }
    all_ok = all(s.status == "ok" for s in services.values())
    any_down = any(s.status == "down" for s in services.values())

    if all_ok:
        overall = "healthy"
    elif any_down:
        overall = "unhealthy"
    else:
        overall = "degraded"

    return HealthResponse(status=overall, version="1.0.0", services=services)