# MentorMind AI — Project Overview

> **AI Personalized Learning & Interview Coach** — a full-stack platform that helps students predict performance, study smarter, practice interviews, and plan careers.

**Repository:** [github.com/Tharmithan/mentor-mind-ai](https://github.com/Tharmithan/mentor-mind-ai)

---

## Objectives

| # | Objective | How we achieve it |
|---|-----------|-------------------|
| 1 | **Predict student outcomes** | ML models (Random Forest / XGBoost) trained on student performance data |
| 2 | **Personalize learning** | Recommendation engine, study planner, weak-subject detection |
| 3 | **Prepare for interviews** | AI mock interviews with scoring, STT, and emotion analysis |
| 4 | **Ground answers in student notes** | RAG pipeline — PDF upload → embeddings → semantic search → chat |
| 5 | **Enable career planning** | Career agent, skill gaps, learning roadmaps, resume analyzer |
| 6 | **Ship production-ready software** | JWT auth, tests, CI, deployment configs, monitoring & MLOps |

---

## Features

### Core AI

| Feature | Description | Route / API |
|---------|-------------|-------------|
| Performance prediction | Predict score, risk level, burnout probability | `POST /api/predict` |
| SHAP explainability | Feature contributions for each prediction | `POST /api/predict/explain` |
| Study recommendations | Weak topics, revision order, daily plan | `POST /api/recommend` |
| AI insights | Cohort-backed trend messages | `GET /api/insights` |

### Learning Assistant (RAG)

| Feature | Description | Route / API |
|---------|-------------|-------------|
| PDF / notes upload | Extract, chunk, index documents | `POST /api/documents/upload` |
| Semantic search | Find relevant passages | `POST /api/documents/search` |
| RAG chat | Q&A grounded in uploaded notes | `POST /api/documents/chat` |
| Study tools | Summarize, quiz, flashcards, explain | `POST /api/study/*` |

### Interview Coach

| Feature | Description | Route / API |
|---------|-------------|-------------|
| Mock interviews | HR, technical, behavioral modes | `POST /api/interview/start` |
| Answer evaluation | Scores + feedback per question | `POST /api/interview/session/{id}/answer` |
| Speech-to-text | Whisper transcription | `POST /api/interview/transcribe` |
| Emotion analysis | Webcam stress / confidence | `POST /api/interview/emotion/analyze` |

### AI Coach & Agents

| Feature | Description | Route / API |
|---------|-------------|-------------|
| Coach dashboard | Scores, charts, skill gaps, reports | `GET /api/coach/overview` |
| Multi-agent chat | Study · Interview · Career · Resume | `POST /api/agents/chat` |
| Personalization | Profiles, embeddings, style-aware recs | `/api/personalization/*` |
| Long-term memory | Progress tracking, context for agents | `/api/memory/*` |

### Production & Ops

| Feature | Description |
|---------|-------------|
| JWT authentication | Register, login, refresh tokens, logout |
| MLOps pipeline | Model registry, experiments, promote to production |
| Monitoring | Prediction logging, user feedback, drift metrics |
| Automated reports | Weekly/monthly PDF + email reports |

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.12, Uvicorn |
| Database | PostgreSQL (Supabase), SQLite (dev) |
| Vector DB | ChromaDB (persistent embeddings) |
| ML | Scikit-learn, XGBoost, SHAP, joblib |
| LLM | OpenAI-compatible API (optional) |
| Embeddings | Sentence Transformers |
| Interview | Whisper, OpenCV, MediaPipe FER |
| Deployment | Vercel, Railway/Render, Docker |
| CI | GitHub Actions (pytest) |

---

## Documentation Map

| Document | Audience | Link |
|----------|----------|------|
| Architecture | Engineers, recruiters | [architecture.md](./architecture.md) |
| AI pipeline diagram | Engineers | [diagrams/ai-pipeline.mmd](./diagrams/ai-pipeline.mmd) |
| Database schema | Backend devs | [database-schema.md](./database-schema.md) |
| API reference | Integrators | [api-reference.md](./api-reference.md) |
| Deployment guide | DevOps | [deployment-guide.md](./deployment-guide.md) |
| User guide | Students, end users | [user-guide.md](./user-guide.md) |
| Developer guide | Contributors | [developer-guide.md](./developer-guide.md) |

---

## Quick Start

```bash
# Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && cp .env.example .env
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend && npm install && npm run dev
```

- **App:** http://localhost:3000  
- **API docs:** http://localhost:8000/docs  
- **Coach hub:** http://localhost:3000/coach  
