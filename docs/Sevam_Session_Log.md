# 🩺 SympDecoder — Full Session Log & Decision Journal

> **Project:** SympDecoder (Sevam) — Personalized Ayurvedic Health Companion
> **Session:** Phase 7 Completion + Vision Expansion + Architecture Decisions
> **GitHub:** github.com/haricodes2970/Sevam

---

## Table of Contents

- [Phase 7 — What Was Built](#phase-7--what-was-built)
- [Phase 7 — Testing Results](#phase-7--testing-results)
- [GitHub Push — Phase 7](#github-push--phase-7)
- [Architecture Decision — MongoDB Atlas](#architecture-decision--mongodb-atlas)
- [Project Status Check](#project-status-check)
- [Vision Expansion — The Big Pivot](#vision-expansion--the-big-pivot)
- [New Product Vision — Personalized Ayurvedic Companion](#new-product-vision--personalized-ayurvedic-companion)
- [LLM Decision — Ollama vs API vs Fine-tuning](#llm-decision--ollama-vs-api-vs-fine-tuning)
- [Knowledge Base Strategy](#knowledge-base-strategy)
- [Final Architecture Decision](#final-architecture-decision)
- [Revised Roadmap](#revised-roadmap)

---

## Phase 7 — What Was Built

**Status:** ✅ Complete — pushed to GitHub at commit `c73d664`

### Files created (20 total)

```
frontend/
├── .env                          VITE_API_URL=http://localhost:8000
├── index.html                    Entry point + Google Fonts (Outfit + IBM Plex Mono)
├── package.json                  React 18, Vite, Tailwind CSS
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── CORS_PATCH.py                 Add localhost:3000 to backend CORS
└── src/
    ├── main.jsx                  React root
    ├── App.jsx
    ├── index.css                 Design tokens + all animations
    ├── api/
    │   └── medicAPI.js           All API calls (sendMessage, feedback, healthCheck)
    ├── components/
    │   ├── Header.jsx            ECG heartbeat logo + API status dot + disclaimer
    │   ├── ChatWindow.jsx        Message list + auto-resize input + suggested prompts
    │   ├── MessageBubble.jsx     User/bot bubbles + severity badge + source chips + feedback
    │   ├── SeverityBadge.jsx     LOW / MEDIUM / HIGH / EMERGENCY coloured pill
    │   ├── TypingIndicator.jsx   3-dot staggered bounce animation
    │   └── EmergencyAlert.jsx    Fullscreen red pulsing overlay + 112/911/108
    └── pages/
        └── ChatPage.jsx          All state management
```

### Design system

```
Aesthetic:      Dark clinical terminal
Background:     #07090f (near black)
Accent:         #00d9a6 (teal)
UI Font:        Outfit
Bot text font:  IBM Plex Mono (medical terminal feel)
```

### Animations built

| Animation | Used on |
|---|---|
| ECG heartbeat | Header logo |
| slideUp | Every new message |
| typingDot (staggered) | 3-dot typing indicator |
| emergencyGlow | Emergency bubble border |
| redPulse | Emergency overlay card |
| cardIn (spring) | Emergency overlay entrance |
| statusBlink | API status dot while connecting |

### How to run

```powershell
# Terminal 1 — Backend
cd "D:\git projects\Sevam\sevam"
venv\Scripts\activate
python run_api.py

# Terminal 2 — Frontend
cd frontend
npm install   # first time only
npm run dev   # → http://localhost:3000
```

---

## Phase 7 — Testing Results

### ✅ UI confirmed working

- Dark clinical UI rendered correctly at localhost:3000
- API Online green dot showing (healthCheck endpoint responding)
- Suggested prompt cards rendering
- Disclaimer bar visible
- Input field + send button working

### ✅ Emergency overlay confirmed working

Tested with: `"my chest hurts and I can't breathe"`

- Full-screen red pulsing overlay triggered
- Siren icon, MEDICAL EMERGENCY heading
- Emergency numbers: 112 / 911 / 108
- Dismiss button working

### 🔧 Bug fixed — markdown in emergency message

**Problem:** Backend response contained raw markdown (`**Please take immediate action:**`)
showing as literal `**` in the overlay.

**Fix applied** to `EmergencyAlert.jsx`:
```javascript
const cleanText = (text = '') =>
  text
    .replace(/\*\*(.*?)\*\*/g, '$1')
    .replace(/\*(.*?)\*/g, '$1')
    .replace(/^\s*[-•]\s/gm, '· ')
    .trim()
```

---

## GitHub Push — Phase 7

```
Commit: beab84f..c73d664  main -> main
Files:  30 objects pushed
Size:   41.49 KiB
```

```powershell
git add .
git commit -m "Phase 7 complete — React frontend (Vite + Tailwind)"
git push origin main
```

**Note:** `node_modules/` must be in `.gitignore` — confirmed before push.

---

## Architecture Decision — MongoDB Atlas

**Decision:** Replace PostgreSQL with MongoDB Atlas for cloud deployment.

**Why:**
```
PostgreSQL (current):
  Local only — hard to deploy to cloud for free
  Requires Alembic migrations for schema changes
  Complex setup on Render free tier

MongoDB Atlas (chosen):
  Free M0 tier — 512MB, always free
  No migrations needed — flexible document model
  Easy environment variable connection string
  Works perfectly with Render deployment
  Motor async driver fits FastAPI perfectly
```

**Files to update:**
```
backend/database/connection.py   → Motor async client
backend/models/db_models.py      → Pydantic document models
backend/services/db_service.py   → MongoDB CRUD operations
requirements.txt                 → swap psycopg2/alembic → motor
```

**Collections (replacing 4 SQL tables):**
```
sessions        { session_id, message_count, is_emergency, created_at }
messages        { session_id, user_message, bot_response, sources, severity }
symptom_logs    { session_id, intent, symptoms, severity_score }
feedback        { session_id, message_id, rating, created_at }
```

**Setup steps:**
1. https://cloud.mongodb.com → free M0 cluster
2. Database Access → add user + password
3. Network Access → Allow from anywhere (0.0.0.0/0)
4. Connect → Drivers → copy connection string
5. Add to `.env`: `MONGODB_URI=mongodb+srv://...`

---

## Project Status Check

```
Phase 0  ✅  Environment setup
Phase 1  ✅  Medical knowledge data layer (10 documents)
Phase 2  ✅  NLP symptom understanding (spaCy)
Phase 3  ✅  RAG knowledge system (ChromaDB + SentenceTransformers)
Phase 4  ✅  LLM chatbot + safety layer (Groq/Llama 3.1)
Phase 5  ✅  FastAPI backend (5 endpoints)
Phase 6  ⚠️  Database layer (built with PostgreSQL → migrating to MongoDB)
Phase 7  ✅  React frontend (live + tested)
Phase 8  🔜  Testing + Docker + Deployment
```

---

## Vision Expansion — The Big Pivot

During this session, the project vision expanded significantly from a simple symptom chatbot to a full personalized Ayurvedic health companion. Here is the complete thought process captured:

### What triggered the pivot

The original SympDecoder answered symptoms from a static JSON knowledge base using a third-party API key (Groq). The concerns raised:

1. **API key dependency** — third-party dependency, potential costs, breaks when service is down
2. **Generic responses** — same answer for everyone regardless of who they are
3. **No food context** — doesn't know what you ate, which causes most everyday symptoms
4. **No personal history** — doesn't know your existing conditions or previous symptoms
5. **Missing Ayurvedic knowledge** — India has thousands of years of medical knowledge being lost
6. **Not a real-world solution** — "just a JSON file giving answers" — not solving a real problem

### The insight about food and symptoms

```
Person eats: deep fried food + cold drink
Reports:     chest pain

Current bot: "Chest pain can be cardiac. Call emergency services."
             → Panic. Unnecessary ER visit.

Ideal bot:   Reads food log → sees heavy oily meal 2 hours ago
             "Based on your food log, this is very likely gastric
              not cardiac. Try ajwain water + warm compress.
              If pain spreads to arm/jaw, seek emergency care."
             → Correct. Calm. Actionable.
```

### Why Ayurveda specifically

- No English medicines before 200 years ago in India
- Vaidyas treated successfully with herbs, diet, lifestyle
- Fewer side effects than pharmaceutical interventions
- Holistic — treats root cause, not just symptom suppression
- Knowledge being lost from everyday life
- Legal boundary — cannot suggest prescription medicines → Ayurveda is the perfect scope

### Legal and ethical boundaries established

```
SympDecoder WILL:
  ✅ Suggest Ayurvedic herbs and preparations
  ✅ Recommend home remedies (turmeric, ginger, etc.)
  ✅ Give dietary guidance
  ✅ Suggest yoga and breathing techniques
  ✅ Recommend consulting an Ayurvedic practitioner
  ✅ Escalate emergencies immediately

SympDecoder WILL NOT:
  ❌ Suggest prescription medicines
  ❌ Make definitive diagnoses
  ❌ Replace professional medical consultation
  ❌ Handle emergencies (escalates immediately)
```

---

## New Product Vision — Personalized Ayurvedic Companion

### The one-line description

**"A personalized Ayurvedic health companion that connects what you eat, who you are, and what you feel — to give you grounded, traditional remedies before reaching for a prescription."**

### Three pillars

#### Pillar 1 — Health Profile (who you are)

Captured at onboarding:
```
- Dosha constitution (Vata / Pitta / Kapha) via questionnaire
- Existing conditions and chronic illnesses
- Known allergies and food intolerances
- Current medications (for herb-drug interaction awareness)
- Age, gender, lifestyle
- Sleep patterns, stress levels, activity level
- Previous symptom history and what worked
```

Every bot response is personalized using this profile.

#### Pillar 2 — Daily Food Diary (what you eat)

```
Not a calorie counter — a symptom correlator.

User logs natural language:
  "Idli chai in morning, rice dal pickle lunch,
   samosa cold drink evening, chapati paneer dinner"

Bot uses this when symptoms are reported.

Tracks:
  - What was eaten and when
  - Meal frequency (irregular eating aggravates Vata)
  - Food qualities (heavy/light, spicy/bland, hot/cold)
  - Weekly patterns — correlates recurring symptoms with diet
```

#### Pillar 3 — Contextual Response Engine

```
Input:  symptom + health profile + recent food log
        ↓
RAG:    retrieve relevant Ayurvedic knowledge
        ↓
LLM:    generate personalized response

Output structure:
  1. Food-symptom connection (if applicable)
  2. Dosha analysis
  3. Ayurvedic explanation of symptom
  4. Home remedy (preparation + dosage)
  5. Dietary guidance for today
  6. Lifestyle adjustment
  7. Yoga/breathing if relevant
  8. Escalation: "If not better in X hours, consult practitioner"
```

### The personalization example

```
Same symptom: "I have a headache"

User A — Vata type, skipped lunch, stressed, 3 hours sleep:
  → Warm sesame oil head massage (Abhyanga)
  → Ashwagandha with warm milk
  → Eat warm food immediately
  → Sleep in a quiet dark room

User B — Pitta type, ate spicy biryani, sun exposure:
  → Cold coconut oil on scalp
  → Coriander and fennel water
  → Avoid sun and screens
  → No spicy food today

Same symptom. Different root cause. Different remedy.
This is what Ayurveda has always known.
```

---

## LLM Decision — Ollama vs API vs Fine-tuning

### Why LLM is necessary at all

```
Without LLM:
  RAG retrieves document → returns raw text
  Output: copy-paste of your knowledge doc
  Not a conversation. Not personalized. Not useful.

With LLM:
  RAG retrieves document → LLM reads it + context
  Output: personalized, conversational, actionable response
  The LLM is the brain that talks intelligently.
```

### All options evaluated

| Option | API Key | Cost | Quality | Complexity |
|---|---|---|---|---|
| Groq API (current) | ✅ Required | Free tier | High | Low |
| Ollama local LLM | ❌ None | Free forever | High | Medium |
| Rule-based (no LLM) | ❌ None | Free | Low | Low |
| Tiny fine-tuned model | ❌ None | Free | Medium-High | High |

### Why rule-based (no LLM) doesn't scale

```
Works for: "I have a headache"
           → maps to headache → returns remedy card

Breaks for: "I feel something weird in my chest
             and my left arm feels heavy since yesterday"
             → rule engine confused — no exact match
             → LLM immediately recognizes cardiac emergency
```

### Final LLM decision — Ollama ✅

**Chosen: Ollama running Llama 3.1 locally**

```
Why Ollama:
  ✅ No API key — fully independent
  ✅ Free forever — no usage costs
  ✅ Works offline after initial download
  ✅ Health data never leaves your machine
  ✅ No third-party service dependency
  ✅ RTX 3050 provides GPU acceleration — fast responses

Hardware check (Asus A15 Tough Gaming):
  RAM:      16GB ✅ Ollama runs comfortably
  SSD:      512GB ✅ Model file ~5GB, plenty of room
  GPU:      RTX 3050 4GB NVIDIA ✅ GPU acceleration
  
After RAM upgrade (planned 32GB):
  ✅ Can run 13B parameter models
  ✅ Fine-tuned model + RAG simultaneously
```

**Installation (one command):**
```powershell
winget install Ollama.Ollama
ollama pull llama3.1
```

**Code change — replace Groq with Ollama:**
```python
# Before (Groq)
from groq import Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# After (Ollama)
import ollama
response = ollama.chat(
    model='llama3.1',
    messages=[{'role': 'user', 'content': prompt}]
)
```

---

## Knowledge Base Strategy

### Current knowledge base (10 documents)

```
doc_001  Chest Pain
doc_002  Headache
doc_003  Fever
doc_004  Sore Throat
doc_005  Stomach Pain and Nausea
doc_006  Back Pain
doc_007  Fatigue and Tiredness
doc_008  Emergency Warning Signs
doc_009  Cough
doc_010  Dizziness
```

### Planned expansion — 20 new documents

#### Ayurvedic remedies per symptom (8 docs)
```
ayu_001  Ayurvedic Headache Remedies
ayu_002  Ayurvedic Fever + Cold Treatment
ayu_003  Ayurvedic Digestive Issues + Acidity
ayu_004  Ayurvedic Cough + Sore Throat
ayu_005  Ayurvedic Fatigue + Low Energy
ayu_006  Ayurvedic Joint + Back Pain
ayu_007  Ayurvedic Skin Issues
ayu_008  Ayurvedic Stress + Anxiety
```

#### Herb and home remedy library (7 docs)
```
herb_001  Turmeric — anti-inflammatory, wound healing, immunity
herb_002  Ginger — nausea, digestion, Vata-Kapha balancing
herb_003  Honey + Tulsi — cough, immunity, respiratory
herb_004  Neem — skin infections, blood purification
herb_005  Ashwagandha — stress, fatigue, strength
herb_006  Ajwain — bloating, acidity, digestion
herb_007  Steam + Salt Water — cold, throat, sinus
```

#### Dosha-based analysis (3 docs)
```
dosha_001  Vata Imbalance — symptoms, causes, remedies
dosha_002  Pitta Imbalance — symptoms, causes, remedies
dosha_003  Kapha Imbalance — symptoms, causes, remedies
```

#### Yoga and breathing (2 docs)
```
yoga_001  Pranayama for headache, anxiety, breathing issues
yoga_002  Therapeutic poses for back pain and fatigue
```

### Knowledge format decision

**NOT Q&A format** — loses important context

**Chosen: Structured rich text format**
```
DISEASE:       Name in English + Ayurvedic name
DOSHA:         Which dosha is aggravated
SYMPTOMS:      How it presents
ROOT CAUSE:    Ayurvedic explanation
HERBS:         Specific herbs + preparation
HOME REMEDY:   Step by step instructions
DIET:          What to eat / avoid
YOGA:          Specific technique
AVOID:         Triggers to eliminate
WHEN TO SEEK:  Clear escalation criteria
```

This preserves all context — dosha relationships, preparation methods, contraindications, philosophy — nothing gets lost.

---

## Final Architecture Decision

### Complete system architecture

```
┌─────────────────────────────────────────────────┐
│              SympDecoder v2.0                    │
│        Personalized Ayurvedic Companion          │
├─────────────────────────────────────────────────┤
│                                                  │
│  React Frontend (Vite + Tailwind)                │
│  ├── Chat Interface         (Phase 7 ✅)         │
│  ├── Food Diary             (Phase 8C 🔜)        │
│  ├── Health Profile         (Phase 8D 🔜)        │
│  └── Symptom History        (Phase 8D 🔜)        │
│                                                  │
│  FastAPI Backend                                 │
│  ├── Chat endpoints         (Phase 5 ✅)         │
│  ├── Food log endpoints     (Phase 8C 🔜)        │
│  ├── User profile endpoints (Phase 8D 🔜)        │
│  └── Context builder        (Phase 8E 🔜)        │
│       profile + food + symptom → unified context │
│                                                  │
│  AI Layer                                        │
│  ├── NLP pipeline           (Phase 2 ✅)         │
│  ├── RAG engine             (Phase 3 ✅)         │
│  ├── Ollama local LLM       (Phase 8F 🔜)        │
│  └── Fine-tuned model       (Phase 9 📅)         │
│                                                  │
│  Database — MongoDB Atlas                        │
│  ├── users                  (Phase 8A 🔜)        │
│  ├── health_profiles        (Phase 8D 🔜)        │
│  ├── food_logs              (Phase 8C 🔜)        │
│  ├── conversations          (Phase 8A 🔜)        │
│  └── symptom_history        (Phase 8D 🔜)        │
│                                                  │
└─────────────────────────────────────────────────┘
```

---

## Revised Roadmap

```
Phase 8A  MongoDB Atlas migration
          Replace PostgreSQL — cloud database
          Collections: users, sessions, messages, feedback

Phase 8B  Ayurveda knowledge base expansion
          20 new documents — herbs, doshas, remedies, yoga
          Re-index ChromaDB after additions

Phase 8C  Food diary feature
          Daily meal logging (natural language)
          Food-symptom correlation engine
          Frontend: food log UI tab

Phase 8D  Health profile + onboarding
          Dosha questionnaire on signup
          Health history storage
          Profile-aware responses

Phase 8E  Context engine
          Unified context: profile + food + symptom
          Personalized RAG retrieval
          Both perspectives: Ayurveda + modern medicine

Phase 8F  Switch to Ollama
          Remove Groq API dependency
          Install: winget install Ollama.Ollama
          Model: llama3.1 (8B, GPU accelerated)
          Zero API keys

Phase 9   Fine-tuning on Google Colab
          Model: Phi-3 Mini or TinyLlama
          Technique: QLoRA (fits on T4 GPU)
          Data: Structured Ayurvedic knowledge
          Result: Custom model that speaks Ayurveda natively

Phase 10  Full deployment
          Backend → Render
          Frontend → Vercel
          DB → MongoDB Atlas (already cloud)
          Vector DB → Pinecone (replace local ChromaDB)
```

---

## Hardware Notes

```
Device:   Asus A15 Tough Gaming Laptop
RAM:      16GB (upgrade to 32GB planned — 15-20 days)
SSD:      512GB
GPU:      NVIDIA RTX 3050 4GB

Ollama assessment:
  Current (16GB):   Llama 3.1 8B runs comfortably
  After upgrade:    Llama 3.1 13B possible
  GPU acceleration: RTX 3050 speeds up inference significantly
  
Fine-tuning assessment (Colab):
  Colab T4:   16GB VRAM
  QLoRA:      ~10-12GB needed — fits comfortably
  Time:       2-4 hours — safe from disconnection
```

---

## Key Decisions Summary

| Decision | Choice | Reason |
|---|---|---|
| Database | MongoDB Atlas | Free cloud tier, no migrations, async with Motor |
| LLM | Ollama (local) | No API key, free forever, GPU accelerated |
| Knowledge format | Rich structured text | Preserves full Ayurvedic context, nothing lost |
| Fine-tuning approach | QLoRA on Colab (Phase 9) | Fits T4 GPU, feasible without disconnecting |
| Deployment | Render + Vercel | Free tier, GitHub auto-deploy |
| Scope boundary | Ayurveda + home remedies only | Legal + ethical — no prescription medicines |
| Personalization | Profile + food diary | Unique differentiator, no other app does this |

---

## Next Immediate Steps

```
You:    Research Ayurvedic content for knowledge base
        Literature survey for gaps
        Set up MongoDB Atlas account (free)

When you return:
  1. MongoDB Atlas migration (connection.py, db_models.py, db_service.py)
  2. Install Ollama + pull llama3.1
  3. Replace Groq → Ollama in llm_client.py
  4. Add 20 Ayurveda documents to knowledge base
  5. Re-index ChromaDB
  6. Deploy to Render + Vercel
```

---

*Session documented: Phase 7 complete → Vision expanded → Ollama chosen → Ayurvedic companion roadmap set*
*GitHub: github.com/haricodes2970/Sevam*
*Next session: MongoDB Atlas + Ollama integration + Ayurveda knowledge base*

