"""
SympDecoder — FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api.middleware.error_handler import ErrorHandlerMiddleware
from backend.api.routes import chat, symptom, knowledge, health, feedback


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🩺 SympDecoder API starting up...")
    print("   Docs: http://localhost:8000/docs")
    yield
    print("🩺 SympDecoder API shutting down.")


app = FastAPI(
    title="SympDecoder — Medical Symptom Triage API",
    description="RAG-powered medical chatbot. Always consult a qualified healthcare professional.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(symptom.router)
app.include_router(knowledge.router)
app.include_router(health.router)
app.include_router(feedback.router)


@app.get("/", tags=["System"])
async def root():
    return {"name": "SympDecoder API", "version": "1.0.0", "status": "running", "docs": "/docs"}