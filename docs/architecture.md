# MentorMind AI — System Architecture

> **Week 7 · Day 7** — Industry-level architecture reference for recruiters, contributors, and production deployment.

---

## 1. Layered Architecture

The platform follows a **modular monolith** with clear separation of concerns:

```
Frontend (Next.js)
        ↓
FastAPI Backend
        ↓
AI Services Layer
        ↓
ML Models + Agents + RAG
        ↓
PostgreSQL + Vector DB
```

### ASCII overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│  FRONTEND — Next.js 16 · TypeScript · Tailwind CSS                      │
│  / · /dashboard · /coach · /assistant · /interview · /planner · /resume │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ REST (JSON) · Axios · CORS
┌───────────────────────────────▼─────────────────────────────────────────┐
│  FASTAPI BACKEND — Python 3.12 · Uvicorn · OpenAPI /docs                │
│  Routes → Services → Domain modules (70+ endpoints)                       │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│  AI SERVICES LAYER                                                      │
│  Multi-Agent Router · Personalization · Memory · Interview · RAG        │
│  Learning Analytics · Reports · MLOps · Monitoring & Feedback           │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│  ML MODELS + AGENTS + RAG                                               │
│  joblib (RF/XGBoost) · SHAP · OpenAI GPT · Sentence Transformers        │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────┐
│  DATA LAYER                                                             │
│  PostgreSQL · ChromaDB · uploads/ JSON stores · ml-models/ artifacts    │
└─────────────────────────────────────────────────────────────────────────┘
```

Full Mermaid diagram: [diagrams/system-architecture.mmd](./diagrams/system-architecture.mmd)

---

## 2. Frontend Architecture

| Route | Purpose |
|-------|---------|
| `/` | Landing page |
| `/dashboard` | ML prediction, analytics, study planner |
| `/coach` | AI Coach hub — scores, personalization, memory, MLOps, monitoring |
| `/assistant` | RAG chat, PDF upload, study tools |
| `/interview` | Mock interview with STT and emotion analysis |
| `/planner` | Personalized learning roadmap |
| `/resume` | ATS resume analyzer |

**Stack:** Next.js 16, TypeScript, Tailwind, Axios (`frontend/src/lib/api.ts`)

---

## 3. Backend Architecture

```
backend/app/
├── main.py              # FastAPI app, 20+ routers
├── routes/              # HTTP controllers
├── services/            # Business orchestration
├── ai/                  # ML predictor, SHAP, insights
├── agents/              # Multi-agent router + collaboration
├── rag/                 # PDF, ChromaDB, study tools
├── interview/           # Sessions, STT, emotion, evaluation
├── personalization/     # Profiles, embeddings, recs
├── memory/              # Long-term memory
├── analytics/           # Learning analytics
├── reports/             # PDF/email reports
├── mlops/               # Model registry, deployment
├── monitoring/          # Feedback loop
└── database/            # SQLAlchemy (optional Postgres)
```

---

## 4. AI Services Layer

| Service | Module | Description |
|---------|--------|-------------|
| Multi-Agent | `agents/` | Study, Interview, Career, Resume routing |
| Personalization | `personalization/` | Style-aware recommendations |
| Memory | `memory/` | Long-term progress and context |
| Interview | `interview/` | Mock sessions, scoring, coaching |
| RAG | `rag/` | PDF → embed → search → chat |
| MLOps | `mlops/` | Versioning, MLflow, promote |
| Monitoring | `monitoring/` | Ratings, drift, improvement loop |

---

## 5. Data Flow Examples

**Prediction:** `POST /api/predict` → `MLPredictor` → log to monitoring → response

**RAG:** Upload PDF → chunk → ChromaDB → semantic search → LLM answer

**Feedback loop:** Thumbs-down on rec → `ImprovementLoop` → filtered next recommendations

---

## 6. Related Documentation

| Document | Contents |
|----------|----------|
| [API Reference](./api-reference.md) | All endpoints |
| [AI Models](./ai-models.md) | ML + LLM catalog |
| [Database Schema](./database-schema.md) | Tables + file stores |
| [Deployment Guide](./deployment-guide.md) | Local → production |
