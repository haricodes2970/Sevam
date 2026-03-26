"""
Sevam API — FastAPI application entry point.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database.connection import connect_to_mongo, close_mongo_connection
from backend.api.middleware.error_handler import ErrorHandlerMiddleware
from backend.api.routes import health, chat, knowledge, feedback
from backend.api.routes import food_log, profile


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MongoDB connection across the application lifecycle."""
    await connect_to_mongo()
    print("Sevam API is ready  ->  http://localhost:8000/docs")
    yield
    await close_mongo_connection()


app = FastAPI(
    title="Sevam API",
    description="Personalized Ayurvedic Health Companion — RAG + Local LLM.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(food_log.router)
app.include_router(profile.router)
app.include_router(feedback.router)


# ── Root ──────────────────────────────────────────────────────────────────────
@app.get("/", tags=["System"])
async def root():
    """API root — quick status check."""
    return {"app": "Sevam", "status": "running", "version": "1.0.0"}
