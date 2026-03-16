import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from backend.models.schemas import KnowledgeSourcesResponse, KnowledgeSource

router = APIRouter()

PROCESSED_CHUNKS_PATH = Path("data/processed/processed_chunks.json")


@router.get("/knowledge-sources", response_model=KnowledgeSourcesResponse, tags=["Knowledge"])
async def get_knowledge_sources() -> KnowledgeSourcesResponse:
    if not PROCESSED_CHUNKS_PATH.exists():
        raise HTTPException(status_code=503, detail="Knowledge base not found.")

    try:
        with open(PROCESSED_CHUNKS_PATH, encoding="utf-8") as f:
            raw_chunks = json.load(f)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse knowledge base: {e}")

    sources = [
        KnowledgeSource(
            chunk_id=chunk.get("chunk_id", ""),
            parent_id=chunk.get("parent_id", ""),
            title=chunk.get("title", "Unknown"),
            source=chunk.get("source", "unknown"),
            chunk_index=chunk.get("chunk_index", 0),
            total_chunks=chunk.get("total_chunks", 1),
            word_count=chunk.get("word_count", 0),
            is_emergency=chunk.get("is_emergency", False),
        )
        for chunk in raw_chunks
    ]

    return KnowledgeSourcesResponse(total=len(sources), sources=sources)