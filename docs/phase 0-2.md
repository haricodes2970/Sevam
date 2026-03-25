# 🩺 Sevam — Project Progress Documentation

> **Project:** SympDecoder — RAG-Powered Medical Symptom Triage Chatbot  
> **Codename:** Sevam  
> **Stack:** Python 3.11, FastAPI, LangChain, spaCy, ChromaDB, FAISS, React  
> **Status:** Phase 0 ✅ | Phase 1 ✅ | Phase 2 ✅ | Phase 3 🔜

---

## Table of Contents

- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Phase 0 — Environment Setup](#phase-0--environment-setup)
- [Phase 1 — Medical Knowledge Data Layer](#phase-1--medical-knowledge-data-layer)
- [Phase 2 — NLP Symptom Understanding](#phase-2--nlp-symptom-understanding)
- [What's Next](#whats-next)

---

## Project Overview

Sevam is an AI-powered medical assistant that helps users understand everyday symptoms using reliable medical knowledge. It uses **Retrieval-Augmented Generation (RAG)** to ground all responses in trusted medical documents — preventing hallucinations.

### How it works (end to end)

```
User types symptom
      ↓
NLP Analyzer (Phase 2)
      ↓
RAG Retrieval (Phase 3)
      ↓
LLM + Safety Layer (Phase 4)
      ↓
Safe grounded response
```

---

## Project Structure

```
Sevam/
└── sevam/
    ├── ai/
    │   ├── __init__.py
    │   ├── embeddings/
    │   │   └── __init__.py
    │   └── symptom_extraction/
    │       ├── __init__.py
    │       ├── intent_classifier.py    ← Phase 2
    │       ├── symptom_extractor.py    ← Phase 2
    │       ├── severity_detector.py    ← Phase 2
    │       └── analyzer.py             ← Phase 2
    ├── backend/
    │   ├── __init__.py
    │   ├── api/
    │   │   ├── __init__.py
    │   │   ├── routes/
    │   │   └── middleware/
    │   ├── models/
    │   │   └── __init__.py
    │   ├── rag_pipeline/
    │   │   └── __init__.py
    │   └── services/
    │       └── __init__.py
    ├── data/
    │   ├── knowledge_sources/
    │   │   └── medical_knowledge.json  ← Phase 1
    │   ├── processed/
    │   │   └── processed_chunks.json   ← Phase 1 output
    │   ├── raw/
    │   ├── cleaner.py                  ← Phase 1
    │   ├── chunker.py                  ← Phase 1
    │   └── ingestion_pipeline.py       ← Phase 1
    ├── docs/
    ├── frontend/
    │   └── src/
    │       ├── components/
    │       └── pages/
    ├── scripts/
    │   └── verify_setup.py             ← Phase 0
    ├── tests/
    ├── venv/                           ← Python 3.11 virtual environment
    ├── .env
    ├── .gitignore
    └── requirements.txt
```

---

## Phase 0 — Environment Setup

**Goal:** Set up a clean, reproducible Python development environment.

**Status:** ✅ Complete

### What was done

- Verified Python 3.11.9 (required — Python 3.14 causes package failures)
- Created project folder structure using PowerShell
- Created Python 3.11 virtual environment (`venv/`)
- Installed all dependencies via `requirements.txt`
- Downloaded spaCy English language model
- Ran verification script — all 15 checks passed

### Key lesson learned

> **Windows note:** PowerShell does not have the `touch` command. Use `New-Item filename -Force` instead.

> **Python version matters:** AI/ML packages like spaCy, numpy, and torch do not support Python 3.14 yet. Always use Python 3.11 for this project.

> **Version pinning:** Do not pin exact package versions (e.g. `fastapi==0.111.0`) — this causes dependency conflicts. Let pip resolve compatible versions automatically.

### Dependencies installed

| Category | Packages |
|---|---|
| API Framework | fastapi, uvicorn, python-dotenv, pydantic |
| RAG & LLM | langchain, langchain-community, langchain-openai, openai |
| Embeddings & Vector DB | sentence-transformers, faiss-cpu, chromadb |
| NLP | spacy, transformers, torch |
| Database | sqlalchemy, psycopg2-binary, alembic |
| Data Processing | beautifulsoup4, requests, pandas, numpy |
| Testing | pytest, httpx |

### Verification output

```
🩺 Sevam — Setup Verification

  ✓  FastAPI
  ✓  LangChain
  ✓  OpenAI client
  ✓  SentenceTransformers
  ✓  FAISS
  ✓  ChromaDB
  ✓  spaCy
  ✓  Transformers (HF)
  ✓  SQLAlchemy
  ✓  Pydantic
  ✓  Requests
  ✓  BeautifulSoup
  ✓  NumPy
  ✓  Pandas

spaCy model check:
  ✓  en_core_web_sm

✅ Done! If all checks pass, you're ready for Phase 1.
```

### How to reactivate environment

```powershell
cd "D:\git projects\Sevam\sevam"
venv\Scripts\activate
```

---

## Phase 1 — Medical Knowledge Data Layer

**Goal:** Build a pipeline that ingests, cleans, chunks, and prepares medical documents for RAG indexing.

**Status:** ✅ Complete

### What was built

```
medical_knowledge.json
        ↓
cleaner.py          — removes noise, normalizes medical abbreviations
        ↓
chunker.py          — splits documents into overlapping word chunks
        ↓
ingestion_pipeline.py — orchestrates all steps end to end
        ↓
processed_chunks.json — 10 clean chunks ready for embedding
```

### Files created

| File | Purpose |
|---|---|
| `data/knowledge_sources/medical_knowledge.json` | 10 curated medical documents |
| `data/cleaner.py` | Text cleaning and normalization |
| `data/chunker.py` | Document chunking with overlap |
| `data/ingestion_pipeline.py` | Full pipeline orchestrator |
| `data/processed/processed_chunks.json` | Pipeline output — RAG-ready chunks |

### Medical knowledge base topics

| ID | Title | Source |
|---|---|---|
| doc_001 | Chest Pain | general_medicine |
| doc_002 | Headache | general_medicine |
| doc_003 | Fever | general_medicine |
| doc_004 | Sore Throat | general_medicine |
| doc_005 | Stomach Pain and Nausea | general_medicine |
| doc_006 | Back Pain | general_medicine |
| doc_007 | Fatigue and Tiredness | general_medicine |
| doc_008 | Emergency Warning Signs | emergency |
| doc_009 | Cough | general_medicine |
| doc_010 | Dizziness | general_medicine |

### Key concepts explained

**Why chunking?**
RAG systems retrieve small pieces of text, not full documents. Chunking splits documents into ~150 word pieces so the retriever can find the exact relevant section.

**Why overlap?**
If an important sentence falls at the boundary of two chunks, overlap (30 words repeated) ensures that sentence appears in at least one chunk fully.

**Why curated data instead of scraping?**
Scraping medical sites like Mayo Clinic has legal restrictions and rate limits. Our curated data is accurate for learning purposes. The pipeline accepts any JSON — swap the file to upgrade data later.

### Pipeline output sample

```json
{
  "chunk_id": "doc_001_chunk_0",
  "parent_id": "doc_001",
  "title": "Chest Pain",
  "source": "general_medicine",
  "chunk_index": 0,
  "total_chunks": 1,
  "content": "Chest pain can have many causes ranging from minor...",
  "word_count": 131,
  "is_emergency": false
}
```

### Pipeline run output

```
🩺 Sevam — Knowledge Ingestion Pipeline

--- Step 1: Loading documents ---
  Loading: data/knowledge_sources/medical_knowledge.json
  Loaded 10 documents

--- Step 2: Cleaning documents ---
  Cleaned: Chest Pain (131 words)
  Cleaned: Headache (130 words)
  ...

--- Step 3: Chunking documents ---
  Chest Pain → 1 chunk(s)
  Headache → 1 chunk(s)
  ...

--- Step 4: Validating ---
  Total chunks: 10
  Removed (too short): 0
  Valid chunks: 10

--- Step 5: Saving ---
  Saved 10 chunks to data/processed/processed_chunks.json

✅ Pipeline complete! Ready for Phase 3 (RAG embeddings).
```

### How to re-run the pipeline

```powershell
cd "D:\git projects\Sevam\sevam"
python data/ingestion_pipeline.py
```

---

## Phase 2 — NLP Symptom Understanding

**Goal:** Build an NLP pipeline that extracts structured information from natural language symptom descriptions.

**Status:** ✅ Complete

### What was built

```
User message: "I've had a bad headache for 3 days"
        ↓
intent_classifier.py   → SYMPTOM_ANALYSIS
symptom_extractor.py   → ["headache", "ache"]
severity_detector.py   → MEDIUM (score: 4)
        ↓
analyzer.py            → combined structured result
```

### Files created

| File | Purpose |
|---|---|
| `ai/symptom_extraction/intent_classifier.py` | Classifies user intent |
| `ai/symptom_extraction/symptom_extractor.py` | Extracts symptoms, triggers, duration, body parts |
| `ai/symptom_extraction/severity_detector.py` | Detects severity level |
| `ai/symptom_extraction/analyzer.py` | Combines all three into one result |

### Intent types

| Intent | When triggered |
|---|---|
| `SYMPTOM_ANALYSIS` | User describes symptoms |
| `EMERGENCY_CHECK` | Emergency keywords detected |
| `GENERAL_INFO` | User asks "what is..." |
| `MEDICATION_QUERY` | User asks about medicine |
| `FOLLOWUP` | Follow-up question |
| `GREETING` | Hello / hi |
| `UNKNOWN` | Unclear input |

### Severity levels

| Level | Score | Meaning |
|---|---|---|
| `LOW` | 1 | Mild, manageable at home |
| `MEDIUM` | 4 | Monitor or see a GP |
| `HIGH` | 7 | Prompt medical attention needed |
| `EMERGENCY` | 10 | Call emergency services now |

### Analyzer output structure

```python
{
    "original_message":    "I have a bad headache for 3 days",
    "intent":              "SYMPTOM_ANALYSIS",
    "intent_confidence":   0.12,
    "symptoms":            ["headache", "ache", "a bad headache"],
    "triggers":            [],
    "duration":            "for 3 days",
    "body_parts":          [],
    "severity":            "MEDIUM",
    "severity_score":      4,
    "severity_indicators": ["for days"],
    "is_emergency":        False
}
```

### Test results

```
Message  : I have a bad headache for 3 days and feel nauseous
Intent   : SYMPTOM_ANALYSIS   Severity: MEDIUM    Emergency: False

Message  : My chest hurts and I can't breathe properly
Intent   : EMERGENCY_CHECK    Severity: EMERGENCY  Emergency: True ⚠️

Message  : I feel a slight sore throat after drinking cold water
Intent   : SYMPTOM_ANALYSIS   Severity: LOW        Emergency: False

Message  : I've been having severe back pain for the past week
Intent   : SYMPTOM_ANALYSIS   Severity: HIGH       Emergency: False

Message  : What is tonsillitis?
Intent   : GENERAL_INFO       Severity: LOW        Emergency: False

Message  : I have fever, chills, and a cough since yesterday
Intent   : SYMPTOM_ANALYSIS   Severity: MEDIUM     Emergency: False
```

### How to run the analyzer

```powershell
cd "D:\git projects\Sevam\sevam"
python ai/symptom_extraction/analyzer.py
```

---

## What's Next

### Phase 3 — RAG Knowledge System 🔜

Take the processed chunks from Phase 1, generate vector embeddings using SentenceTransformers, store them in ChromaDB, and build semantic retrieval.

```
processed_chunks.json
        ↓
SentenceTransformers    — convert text to vectors
        ↓
ChromaDB                — store and index vectors
        ↓
Semantic search         — find relevant chunks for any query
```

### Phase 4 — LLM Chatbot + Safety Layer
### Phase 5 — FastAPI Backend
### Phase 6 — Database Layer
### Phase 7 — React Frontend
### Phase 8 — Testing + Deployment

---

*Last updated: Phase 2 complete — ready for Phase 3*

