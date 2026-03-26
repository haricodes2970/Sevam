"""
Health-check endpoint for the Sevam API.

GET /health-check
  - Pings MongoDB Atlas and reports connection status
  - Returns app name, version, and overall health status
"""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.database.connection import get_database

router = APIRouter(tags=["System"])


class ServiceStatus(BaseModel):
    status: str               # "ok" | "down"
    detail: str | None = None


class HealthResponse(BaseModel):
    app: str
    version: str
    status: str               # "healthy" | "unhealthy"
    services: dict[str, ServiceStatus]


async def _check_mongodb() -> ServiceStatus:
    """Ping the MongoDB Atlas deployment and return its status."""
    try:
        db = get_database()
        await db.client.admin.command("ping")
        return ServiceStatus(status="ok", detail="MongoDB Atlas reachable")
    except Exception as exc:
        return ServiceStatus(status="down", detail=str(exc))


@router.get("/health-check", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return the health of the Sevam API and its dependencies.

    Checks:
      - MongoDB Atlas connectivity via ping command

    Returns:
      overall status = "healthy" only when all services report "ok".
    """
    mongodb_status = await _check_mongodb()

    services = {"mongodb": mongodb_status}
    overall = "healthy" if mongodb_status.status == "ok" else "unhealthy"

    return HealthResponse(
        app="Sevam",
        version="1.0.0",
        status=overall,
        services=services,
    )
