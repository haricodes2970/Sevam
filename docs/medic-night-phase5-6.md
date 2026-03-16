# 🩺 Medic Night — Project Progress Documentation

> **Project:** SympDecoder — RAG-Powered Medical Symptom Triage Chatbot
> **Codename:** Medic Night
> **Stack:** Python 3.11, FastAPI, LangChain, spaCy, ChromaDB, FAISS, Groq (Llama 3.1), React
> **Status:** Phase 0 ✅ | Phase 1 ✅ | Phase 2 ✅ | Phase 3 ✅ | Phase 4 ✅ | Phase 5 ✅ | Phase 6 ✅ | Phase 7 🔜

---

## Table of Contents

- [Project Overview](#project-overview)
- [Phase 5 — FastAPI Backend](#phase-5--fastapi-backend)
- [Phase 6 — PostgreSQL Database Layer](#phase-6--postgresql-database-layer)
- [Errors and Fixes](#errors-and-fixes)
- [What's Next](#whats-next)

---

## Project Overview

Medic Night is an AI-powered medical assistant that helps users understand everyday symptoms using reliable medical knowledge. It uses **Retrieval-Augmented Generation (RAG)** to ground all responses in trusted medical documents — preventing hallucinations.

### Full pipeline (end to end)

```
User types symptom
      ↓
Safety Guard         ← emergency check first, always
      ↓
NLP Analyzer         ← intent + symptoms + severity
      ↓
RAG Retriever        ← top 3 relevant medical chunks
      ↓
Prompt Builder       ← RAG prompt with context + history
      ↓
Groq LLM             ← Llama 3.1 generates response
      ↓
Safety Wrapper       ← disclaimer + emergency escalation
      ↓
save_message()       ← persisted to PostgreSQL
      ↓
Safe grounded answer
```

---

## Phase 5 — FastAPI Backend

**Status:** ✅ Complete

### What was built

Wrapped the entire Phase 1–4 chatbot pipeline in a production REST API using FastAPI.

```
run_api.py
      ↓
backend/api/main.py         ← FastAPI app + lifespan + CORS
      ↓
error_handler.py            ← global exception middleware
      ↓
routes/health.py            ← GET  /health-check
routes/knowledge.py         ← GET  /knowledge-sources
routes/symptom.py           ← POST /analyze-symptom (NLP only)
routes/chat.py              ← POST /chat (full pipeline)
      ↓
models/schemas.py           ← all Pydantic request/response models
      ↓
Swagger UI at /docs         ← test all endpoints in browser
```

### Files created

| File | Purpose |
|---|---|
| `run_api.py` | Uvicorn entrypoint — run with `python run_api.py` |
| `backend/api/main.py` | FastAPI app, CORS, middleware, route registration |
| `backend/api/middleware/__init__.py` | Package init |
| `backend/api/middleware/error_handler.py` | Global unhandled exception → JSON error |
| `backend/api/routes/__init__.py` | Package init |
| `backend/api/routes/chat.py` | POST /chat — full Safety → NLP → RAG → LLM pipeline |
| `backend/api/routes/health.py` | GET /health-check — checks data layer, vector DB, NLP |
| `backend/api/routes/knowledge.py` | GET /knowledge-sources — lists all indexed medical chunks |
| `backend/api/routes/symptom.py` | POST /analyze-symptom — NLP only, no LLM |
| `backend/models/schemas.py` | All Pydantic request/response models |

### Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health-check` | Checks data layer + vector DB + NLP status |
| `GET` | `/knowledge-sources` | Lists all 10 indexed medical chunks |
| `POST` | `/analyze-symptom` | NLP pipeline only — fast, no LLM call |
| `POST` | `/chat` | Full pipeline — Safety → NLP → RAG → LLM |

### How to run

```powershell
cd "D:\git projects\MedicNight\medic-night"
venv\Scripts\activate
python run_api.py
```

Open: **http://localhost:8000/docs**

### Chat endpoint test result

```json
{
  "response": "Chest pain after meals is commonly associated with acid reflux (GERD)...",
  "sources": ["Chest Pain"],
  "severity": "LOW",
  "is_emergency": false,
  "session_id": "9c36fb69-944e-46d5-9145-840e8270c8ab"
}
```

**Verification:**
- ✅ Response generated — grounded GERD explanation
- ✅ Sources cited — RAG retrieved "Chest Pain" chunk
- ✅ Severity detected — LOW (correct)
- ✅ Emergency flag — false (correct)
- ✅ Session ID assigned — conversation tracking ready
- ✅ Safety disclaimer — appended automatically

---

## Phase 6 — PostgreSQL Database Layer

**Status:** ✅ Complete

### What was built

```
alembic.ini + migrations/
      ↓
database/connection.py      ← SQLAlchemy engine + session factory
      ↓
models/db_models.py         ← 4 ORM tables
      ↓
services/db_service.py      ← all CRUD operations
      ↓
routes/feedback.py          ← POST /feedback endpoint
      ↓
PostgreSQL — medicnight DB  ← 4 tables live on port 5432
```

### Files created

| File | Purpose |
|---|---|
| `alembic.ini` | Alembic migration config |
| `backend/database/__init__.py` | Package init |
| `backend/database/connection.py` | SQLAlchemy engine, SessionLocal, Base, get_db() |
| `backend/database/migrations/` | Alembic migrations folder |
| `backend/database/migrations/versions/32c51024e1ae_initial_schema.py` | Auto-generated migration |
| `backend/models/db_models.py` | 4 ORM models |
| `backend/services/db_service.py` | All CRUD operations |
| `backend/api/routes/feedback.py` | POST /feedback endpoint |

### Database tables

| Table | Stores |
|---|---|
| `sessions` | One row per conversation — tracks session_id, message count, emergency flag |
| `messages` | Every user + bot message pair, sources used, severity, emergency flag |
| `symptom_logs` | Structured NLP output per message — intent, symptoms, triggers, severity score |
| `feedback` | User ratings on responses — HELPFUL / NOT_HELPFUL / INACCURATE / EMERGENCY_MISSED |

### Full endpoint list after Phase 6

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health-check` | Service health |
| `GET` | `/knowledge-sources` | List knowledge base |
| `POST` | `/analyze-symptom` | NLP analysis only |
| `POST` | `/chat` | Full pipeline + DB save |
| `POST` | `/feedback` | Rate a bot response |

### How to run migrations

```powershell
# Initialize (run once)
alembic init backend/database/migrations

# Generate migration
alembic revision --autogenerate -m "initial schema"

# Apply migration
alembic upgrade head
```

### PostgreSQL verification

```sql
medicnight=# \dt

               List of tables
 Schema |      Name       | Type  |  Owner
--------+-----------------+-------+----------
 public | alembic_version | table | postgres
 public | feedback        | table | postgres
 public | messages        | table | postgres
 public | sessions        | table | postgres
 public | symptom_logs    | table | postgres
(5 rows)
```

---

## Errors and Fixes

### Error 1 — Git wipe (critical)

**What happened:**
Running `git reset --hard` + `git clean -fd` wiped all Phase 5 and Phase 6 files because they had not been committed.

**Files lost:**
```
run_api.py
backend/api/main.py
backend/api/middleware/ (all files)
backend/api/routes/ (all files)
backend/database/ (all files)
backend/models/db_models.py
backend/models/schemas.py
backend/services/db_service.py
alembic.ini
frontend/
tests/
data/raw/
```

**Fix:**
Recreated all files manually from scratch.

**Prevention:**
```powershell
# Always commit after completing each phase
git add .
git commit -m "Phase 5 complete — FastAPI backend"
git push
```

---

### Error 2 — Typo in filename

**What happened:**
`backend/api/main.py` was created as `backend/api/maun.py` — typo in filename caused import failure.

**Error:**
```
ModuleNotFoundError: No module named 'backend.api.main'
```

**Fix:**
```powershell
Rename-Item backend\api\maun.py main.py
```

---

### Error 3 — Empty middleware file

**What happened:**
`backend/api/middleware/error_handler.py` existed but was empty — no class inside.

**Error:**
```
ImportError: cannot import name 'ErrorHandlerMiddleware' from
'backend.api.middleware.error_handler'
```

**Fix:**
Added the `ErrorHandlerMiddleware` class to the file:

```python
from starlette.middleware.base import BaseHTTPMiddleware

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            ...
```

---

### Error 4 — Empty route files

**What happened:**
All files in `backend/api/routes/` existed but were empty — no `router` object inside any of them.

**Error:**
```
AttributeError: module 'backend.api.routes.chat' has no attribute 'router'
```

**Fix:**
Populated all route files with their correct content including `router = APIRouter()`.

---

### Error 5 — psql not recognized in PowerShell

**What happened:**
PostgreSQL was installed at `D:\Applications\PostgresSQL\` but the `bin` folder was not added to the system PATH.

**Error:**
```
psql : The term 'psql' is not recognized as the name of a cmdlet
```

**Fix (temporary — per session):**
```powershell
$env:PATH += ";D:\Applications\PostgresSQL\bin"
```

**Fix (permanent):**
```
Windows Search → "Edit the system environment variables"
→ Environment Variables → System Variables → Path → Edit → New
→ paste: D:\Applications\PostgresSQL\bin
→ OK → OK → OK
```

---

### Error 6 — Wrong password in DATABASE_URL

**What happened:**
Password contained `@` character which broke the PostgreSQL connection URL format.

**Error:**
```
psycopg2.OperationalError: could not translate host name "7078@localhost"
to address: Non-recoverable failure in name resolution
```

**Root cause:**
URL parser treated `@` in password as the host separator, turning:
```
postgresql://postgres:pass@7078@localhost:5432/medicnight
```
into an invalid host `7078@localhost`.

**Fix:**
URL-encode `@` as `%40` in the password.

In `.env`:
```env
DATABASE_URL=postgresql://postgres:pass%40word@localhost:5432/medicnight
```

---

### Error 7 — % character in alembic.ini

**What happened:**
After fixing the `@` → `%40` in `alembic.ini`, the `%` character itself broke the Python configparser.

**Error:**
```
configparser.InterpolationSyntaxError: '%' must be followed by '%' or '(',
found: '%407078@localhost:5432/medicnight'
```

**Root cause:**
`alembic.ini` uses Python's configparser which treats `%` as an interpolation character. Single `%` must be escaped as `%%`.

**Fix:**
In `alembic.ini` only (not in `.env`):
```ini
sqlalchemy.url = postgresql://postgres:pass%%40word@localhost:5432/medicnight
```

Note: `.env` keeps single `%40`. Only `alembic.ini` needs `%%40`.

---

### Error 8 — Alembic ran but created no tables

**What happened:**
Running `alembic upgrade head` without first generating a migration file produced no output and created no tables.

**Error:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
(no tables created)
```

**Root cause:**
`alembic upgrade head` applies existing migrations — but no migration file existed yet in `versions/`.

**Fix:**
Generate the migration first, then apply:
```powershell
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

---

### Error 9 — alembic command run inside psql prompt

**What happened:**
Ran `alembic upgrade head` while still inside the PostgreSQL interactive shell.

**Symptom:**
```
medicnight=# alembic upgrade head
medicnight-#
```
The command was silently accepted as SQL input, not executed.

**Fix:**
Exit psql first:
```sql
\q
```
Then run alembic in PowerShell.

---

## What's Next

### Phase 7 — React Frontend 🔜

Chat UI with message bubbles, severity badges, emergency alerts, and source citations.

```
React + Tailwind
      ↓
Chat interface
Severity badges     ← LOW / MEDIUM / HIGH / EMERGENCY
Emergency alerts    ← full-screen warning
Source citations    ← shows which medical docs were used
Feedback buttons    ← thumbs up/down per response
```

### Phase 8 — Testing + Docker + Deployment

```
pytest              ← unit + integration tests
Docker              ← containerize backend + frontend
Vercel              ← deploy frontend
Render              ← deploy backend
Pinecone/Chroma     ← cloud vector DB
PostgreSQL          ← cloud database (Railway / Supabase)
```

---

## Quick Start (from scratch)

```powershell
# 1. Navigate and activate
cd "D:\git projects\MedicNight\medic-night"
& "d:\git projects\MedicNight\medic-night\venv\Scripts\Activate.ps1"

# 2. Add PostgreSQL to PATH (until permanent fix applied)
$env:PATH += ";D:\Applications\PostgresSQL\bin"

# 3. Start API
python run_api.py
```

Open **http://localhost:8000/docs** to test all endpoints.

---

## Commit History

```
Phase 5 + 6 complete — FastAPI backend + PostgreSQL database layer
```

---

*Last updated: Phase 6 complete — ready for Phase 7 (React Frontend)*
