# 🩺 Medic Night — Project Progress Documentation

> **Project:** SympDecoder — RAG-Powered Medical Symptom Triage Chatbot  
> **Codename:** Medic Night  
> **Stack:** Python 3.11, FastAPI, LangChain, spaCy, ChromaDB, FAISS, Groq (Llama 3.1), React  
> **Status:** Phase 0 ✅ | Phase 1 ✅ | Phase 2 ✅ | Phase 3 ✅ | Phase 4 ✅ | Phase 5 🔜

---

## Table of Contents

- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Phase 0 — Environment Setup](#phase-0--environment-setup)
- [Phase 1 — Medical Knowledge Data Layer](#phase-1--medical-knowledge-data-layer)
- [Phase 2 — NLP Symptom Understanding](#phase-2--nlp-symptom-understanding)
- [Phase 3 — RAG Knowledge System](#phase-3--rag-knowledge-system)
- [Phase 4 — LLM Chatbot + Safety Layer](#phase-4--llm-chatbot--safety-layer)
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
Safe grounded answer
```

---

## Project Structure

```
MedicNight/
└── medic-night/
    ├── ai/
    │   ├── __init__.py
    │   ├── embeddings/
    │   │   ├── __init__.py
    │   │   └── embedder.py             ← Phase 3
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
    │   │   ├── __init__.py
    │   │   ├── vector_store.py         ← Phase 3
    │   │   ├── indexer.py              ← Phase 3
    │   │   └── retriever.py            ← Phase 3
    │   └── services/
    │       ├── __init__.py
    │       ├── llm_client.py           ← Phase 4 (Groq/Llama 3.1)
    │       ├── safety_guard.py         ← Phase 4
    │       ├── prompt_builder.py       ← Phase 4
    │       └── chatbot.py              ← Phase 4
    ├── data/
    │   ├── knowledge_sources/
    │   │   └── medical_knowledge.json  ← Phase 1
    │   ├── processed/
    │   │   └── processed_chunks.json   ← Phase 1 output
    │   ├── vector_db/                  ← Phase 3 (ChromaDB data)
    │   ├── raw/
    │   ├── cleaner.py                  ← Phase 1
    │   ├── chunker.py                  ← Phase 1
    │   └── ingestion_pipeline.py       ← Phase 1
    ├── docs/
    │   └── progress.md
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

**Status:** ✅ Complete

### What was done

- Verified Python 3.11.9 (required — Python 3.14 causes package build failures)
- Created project folder structure using PowerShell
- Created Python 3.11 virtual environment (`venv/`)
- Installed all dependencies via `requirements.txt`
- Downloaded spaCy English language model `en_core_web_sm`
- Ran verification script — all 15 checks passed

### Key lessons learned

> **Windows:** PowerShell has no `touch` command. Use `New-Item filename -Force` instead.

> **Python version:** Use Python 3.11 only. AI/ML packages (spaCy, numpy, torch) do not support 3.14 yet.

> **Version pinning:** Never pin exact versions in requirements.txt — causes dependency conflicts. Let pip resolve automatically.

### How to reactivate environment

```powershell
cd "D:\git projects\MedicNight\medic-night"
venv\Scripts\activate
```

---

## Phase 1 — Medical Knowledge Data Layer

**Status:** ✅ Complete

### Pipeline

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

### Medical knowledge base (10 documents)

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

### How to re-run pipeline

```powershell
python data/ingestion_pipeline.py
```

---

## Phase 2 — NLP Symptom Understanding

**Status:** ✅ Complete

### What was built

```
User message
      ↓
intent_classifier.py   → SYMPTOM_ANALYSIS / EMERGENCY / GENERAL_INFO
symptom_extractor.py   → ["headache", "fever", "cough"]
severity_detector.py   → LOW / MEDIUM / HIGH / EMERGENCY
      ↓
analyzer.py            → single combined structured result
```

### Intent types

| Intent | Trigger |
|---|---|
| `SYMPTOM_ANALYSIS` | User describes symptoms |
| `EMERGENCY_CHECK` | Emergency keywords detected |
| `GENERAL_INFO` | "What is..." questions |
| `MEDICATION_QUERY` | Questions about medicine |
| `GREETING` | Hello / hi |
| `UNKNOWN` | Unclear input |

### Severity levels

| Level | Score | Meaning |
|---|---|---|
| `LOW` | 1 | Mild, manageable at home |
| `MEDIUM` | 4 | Monitor or see a GP |
| `HIGH` | 7 | Prompt medical attention needed |
| `EMERGENCY` | 10 | Call emergency services now |

### How to run

```powershell
python ai/symptom_extraction/analyzer.py
```

---

## Phase 3 — RAG Knowledge System

**Status:** ✅ Complete

### How it works

```
INDEXING (runs once):
processed_chunks.json → SentenceTransformers → vectors → ChromaDB

QUERYING (every message):
user query → embed with same model → similarity search → top 3 chunks
```

### Model used

`all-MiniLM-L6-v2` — 384-dimension vectors, fast, accurate, free

### Files

| File | Purpose |
|---|---|
| `ai/embeddings/embedder.py` | Converts text to vectors |
| `backend/rag_pipeline/vector_store.py` | ChromaDB wrapper |
| `backend/rag_pipeline/indexer.py` | Builds the vector index (run once) |
| `backend/rag_pipeline/retriever.py` | Retrieves chunks per query |

### How to re-index

```powershell
python backend/rag_pipeline/indexer.py
```

### Retrieval test results

```
Query: "I have a severe headache and feel dizzy"
  [1] Dizziness        (similarity: 0.31)
  [2] Headache         (similarity: 0.19)
  [3] Emergency Signs  (similarity: 0.17)

Query: "my chest hurts when I breathe"
  [1] Chest Pain       (similarity: 0.49) ✅

Query: "sore throat and difficulty swallowing"
  [1] Sore Throat      (similarity: 0.50) ✅
```

---

## Phase 4 — LLM Chatbot + Safety Layer

**Status:** ✅ Complete

### LLM decision

| Option | Reason rejected / chosen |
|---|---|
| HuggingFace free tier | ❌ Shut down api-inference.huggingface.co (410 gone) |
| HuggingFace router | ❌ Requires paid provider subscription |
| **Groq (Llama 3.1 8B)** | ✅ Free, no credit card, fast, reliable |

### Files

| File | Purpose |
|---|---|
| `backend/services/llm_client.py` | Groq API wrapper (Llama 3.1-8b-instant) |
| `backend/services/safety_guard.py` | Emergency detection + disclaimer |
| `backend/services/prompt_builder.py` | RAG prompt with context + history |
| `backend/services/chatbot.py` | Main pipeline orchestrator |

### Safety guardrails

- Emergency symptoms trigger immediate escalation — no LLM call
- All responses get a medical disclaimer appended
- Prompt injection attempts are sanitized
- Definitive diagnosis language is flagged
- Conversation history capped at 10 turns

### Chatbot test results

```
👤 I have a bad headache for 3 days
🤖 Grounded response with tension/migraine/dehydration causes ✅
   Sources: ['Headache'] | Severity: MEDIUM

👤 Could it be related to stress?
🤖 Remembered context, explained stress-tension link ✅
   Conversational memory working

👤 I also feel dizzy sometimes
🤖 Retrieved Dizziness doc, listed causes ✅
   Sources: ['Dizziness']

👤 My chest hurts and I can't breathe
🤖 ⚠️ EMERGENCY DETECTED — call 911/999/112 immediately ✅
   No LLM call made, emergency response served instantly
```

### How to run chatbot

```powershell
python backend/services/chatbot.py
```

### .env required keys

```env
HF_TOKEN=hf_your_token_here         # HuggingFace (for embeddings)
GROQ_API_KEY=gsk_your_key_here      # Groq (for LLM)
```

---

## What's Next

### Phase 5 — FastAPI Backend 🔜

Wrap the chatbot in a production REST API.

```
POST /chat               ← main chat endpoint
POST /analyze-symptom    ← NLP analysis only
GET  /knowledge-sources  ← list indexed documents
GET  /health-check       ← server health
```

### Phase 6 — Database Layer
Store conversations, symptom logs, and user feedback in PostgreSQL.

### Phase 7 — React Frontend
Chat UI with message bubbles, emergency alerts, and source citations.

### Phase 8 — Testing + Deployment
Docker, Vercel (frontend), Render (backend).

---

## Quick Start (from scratch)

```powershell
# 1. Activate environment
cd "D:\git projects\MedicNight\medic-night"
venv\Scripts\activate

# 2. Re-run data pipeline (if needed)
python data/ingestion_pipeline.py

# 3. Re-index vector DB (if needed)
python backend/rag_pipeline/indexer.py

# 4. Run chatbot test
python backend/services/chatbot.py
```

---

*Last updated: Phase 4 complete — ready for Phase 5 (FastAPI Backend)*
