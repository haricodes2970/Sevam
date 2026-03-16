# ── CORS patch for Phase 7 React frontend ──────────────────────────
# Add / update the CORSMiddleware block in backend/api/main.py
# to include http://localhost:3000 in allowed origins.
#
# Find the existing add_middleware(CORSMiddleware, ...) call and
# replace it with the block below:

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # React dev server  ← ADD THIS
        "http://localhost:5173",   # Vite default (fallback)
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# If no CORSMiddleware block exists yet, paste the block above
# immediately after `app = FastAPI(...)` in main.py.
