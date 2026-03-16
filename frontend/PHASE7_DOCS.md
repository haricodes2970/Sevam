# 🩺 Medic Night — Phase 7: React Frontend

> **Project:** SympDecoder — RAG-Powered Medical Symptom Triage Chatbot
> **Stack:** React 18 · Vite · Tailwind CSS · Outfit + IBM Plex Mono fonts
> **Status:** Phase 7 ✅ Complete

---

## What Was Built

A production-grade React chat interface that connects to the Phase 5 FastAPI backend.

```
frontend/
├── index.html                        ← entry, Google Fonts
├── package.json                      ← React 18, Vite, Tailwind
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── .env                              ← VITE_API_URL=http://localhost:8000
├── CORS_PATCH.py                     ← add localhost:3000 to backend CORS
└── src/
    ├── main.jsx                      ← React root
    ├── App.jsx
    ├── index.css                     ← design tokens, animations, components
    ├── api/
    │   └── medicAPI.js               ← all API calls (sendMessage, feedback, etc.)
    ├── components/
    │   ├── Header.jsx                ← logo + API status dot + disclaimer badge
    │   ├── ChatWindow.jsx            ← scrollable messages + input bar + prompts
    │   ├── MessageBubble.jsx         ← user / bot bubbles with sources + feedback
    │   ├── TypingIndicator.jsx       ← animated 3-dot loader
    │   ├── SeverityBadge.jsx         ← LOW / MEDIUM / HIGH / EMERGENCY pill
    │   └── EmergencyAlert.jsx        ← fullscreen red overlay with dial numbers
    └── pages/
        └── ChatPage.jsx              ← root page, all state management
```

---

## Design System

### Aesthetic: Dark Clinical Terminal

Dark background (`#07090f`) with teal accent (`#00d9a6`).
Two font families:
- **Outfit** — UI labels, inputs, metadata
- **IBM Plex Mono** — bot response text (medical terminal feel)

### Color Tokens (CSS variables in `index.css`)

| Token             | Value       | Usage                       |
|-------------------|-------------|-----------------------------|
| `--bg-primary`    | `#07090f`   | App background              |
| `--bg-card`       | `#111825`   | Bot message bubbles         |
| `--accent`        | `#00d9a6`   | Logo, borders, send button  |
| `--sev-low`       | `#22c55e`   | LOW severity badge          |
| `--sev-medium`    | `#f59e0b`   | MEDIUM severity badge       |
| `--sev-high`      | `#f97316`   | HIGH severity badge         |
| `--sev-emergency` | `#ef4444`   | EMERGENCY badge + overlay   |

### Animations

| Name           | Used on                                   |
|----------------|-------------------------------------------|
| `slideUp`      | Every new message bubble                  |
| `heartbeat`    | Header ECG logo                           |
| `typingDot`    | Three-dot typing indicator                |
| `emergencyGlow`| Emergency bubble border pulse             |
| `redPulse`     | Emergency overlay card glow               |
| `cardIn`       | Emergency overlay entrance (spring curve) |
| `statusBlink`  | API status dot while connecting           |

---

## Component Reference

### `Header.jsx`
- Animated ECG heartbeat SVG (CSS animation)
- Live API status dot — calls `GET /health-check` on mount
- "Not a substitute for medical advice" warning badge
- Accent gradient rule beneath header

### `ChatWindow.jsx`
- Empty state with 6 suggested-prompt cards
- Auto-scroll to bottom on each new message
- Auto-expanding textarea (rows grow up to 3 lines)
- Enter to send, Shift+Enter for new line
- Spinner in send button while `isLoading`

### `MessageBubble.jsx`
- **User:** right-aligned teal gradient bubble
- **Bot:** dark card with monospace text
  - Severity badge in top-left
  - Source chips for RAG citations (e.g. "Chest Pain")
  - 👍 / 👎 feedback buttons → `POST /feedback`
  - HIGH severity: orange border glow
  - EMERGENCY severity: red pulsing border

### `EmergencyAlert.jsx`
- Full-screen overlay with blur backdrop
- Spring-curve card entrance animation
- Pulsing red glow on card
- Emergency numbers: 112 · 911 · 108
- Dismiss button

### `SeverityBadge.jsx`
- Coloured pill with icon + label
- LOW `●` / MEDIUM `◆` / HIGH `▲` / EMERGENCY `⚠`

### `TypingIndicator.jsx`
- Three dots, staggered bounce animation (200ms offset each)

---

## API Layer (`src/api/medicAPI.js`)

| Function           | Endpoint              | Description                |
|--------------------|-----------------------|----------------------------|
| `sendMessage`      | `POST /chat`          | Full pipeline              |
| `analyzeSymptom`   | `POST /analyze-symptom` | NLP only               |
| `submitFeedback`   | `POST /feedback`      | Rate a response            |
| `getKnowledgeSources` | `GET /knowledge-sources` | List indexed docs   |
| `healthCheck`      | `GET /health-check`   | Check backend status       |

---

## Setup and Run

### 1. Apply CORS patch to the backend

Open `backend/api/main.py` and add `http://localhost:3000` to the CORSMiddleware origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # ← add this
        "http://localhost:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Start the backend

```powershell
cd "D:\git projects\MedicNight\medic-night"
venv\Scripts\activate
python run_api.py
# → http://localhost:8000
```

### 3. Install frontend dependencies

```powershell
cd frontend
npm install
```

### 4. Start the frontend

```powershell
npm run dev
# → http://localhost:3000
```

### 5. Build for production

```powershell
npm run build
# Output: frontend/dist/
```

---

## State Flow

```
User types message
        ↓
ChatWindow.onSend(text)
        ↓
ChatPage.handleSend(text)
        ↓
optimistic user bubble added to messages[]
        ↓
sendMessage(text, sessionId)  →  POST /chat
        ↓
backend: Safety → NLP → RAG → Groq LLM → DB save
        ↓
{ response, sources, severity, is_emergency, session_id }
        ↓
is_emergency?  → show EmergencyAlert overlay
        ↓
bot bubble added to messages[]
        ↓
MessageBubble renders with SeverityBadge + SourceChips + Feedback
```

---

## What's Next

### Phase 8 — Testing + Docker + Deployment

```
pytest          ← unit tests (NLP, RAG, API)
pytest-cov      ← coverage report
Docker          ← Dockerfile + docker-compose for backend + frontend
Vercel          ← deploy React frontend
Render          ← deploy FastAPI backend
Neon/Supabase   ← managed PostgreSQL
Pinecone        ← managed vector DB (replace local ChromaDB)
```

---

## Commit

```powershell
git add .
git commit -m "Phase 7 complete — React frontend"
git push
```

---

*Last updated: Phase 7 complete — ready for Phase 8 (Testing + Docker + Deployment)*
