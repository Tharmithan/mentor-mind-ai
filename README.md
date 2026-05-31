# MentorMind AI

**AI Personalized Learning & Interview Coach** — an AI-powered platform that helps students improve learning performance, prepare for interviews, analyze confidence, and receive personalized study recommendations.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Stack](https://img.shields.io/badge/stack-Next.js%20%7C%20FastAPI%20%7C%20PostgreSQL-6366f1)

---

## Project Overview

MentorMind AI combines machine learning, computer vision, and large language models into a single learning companion. Students get performance predictions, tailored study plans, mock interviews with feedback, real-time confidence analysis, career guidance, and a RAG-based PDF learning assistant.

**Repository:** [mentor-mind-ai](https://github.com/Tharmithan/mentor-mind-ai)

---

## Features

| Feature | Description |
|--------|-------------|
| **Student Performance Prediction** | ML models predict outcomes and highlight at-risk areas |
| **Personalized Study Planner** | Weak-topic detection and revision recommendations |
| **AI Mock Interview** | AI-generated questions, speech-to-text, voice interaction, scoring |
| **Emotion & Confidence Detection** | Webcam-based stress and confidence analysis |
| **Career Recommendation Engine** | Data-driven career path suggestions |
| **MLOps Pipeline** | Model versioning, MLflow experiments, deployment promotion |
| **Monitoring & Feedback** | User ratings, prediction drift, continuous improvement loop |
| **AI Coach Dashboard** | Unified hub — scores, personalization, memory, analytics, reports |
| **RAG PDF Learning Assistant** | Upload PDFs, semantic search, contextual Q&A |

---

## Tech Stack

| Layer | Technologies |
|-------|----------------|
| **Frontend** | Next.js 16, TypeScript, Tailwind CSS |
| **Backend** | FastAPI, Python 3.12 |
| **Database** | PostgreSQL (Supabase) |
| **AI/ML** | PyTorch, Scikit-learn, Hugging Face, OpenCV, MediaPipe |
| **Deployment** | Vercel (frontend), Railway (backend), Docker |

---

## Architecture

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

### Documentation (Week 7 · Day 7)

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | Layered system design + data flows |
| [API Reference](docs/api-reference.md) | Complete REST API catalog |
| [AI Models](docs/ai-models.md) | ML models, LLM, agents, embeddings |
| [Database Schema](docs/database-schema.md) | PostgreSQL + ChromaDB + file stores |
| [Deployment Guide](docs/deployment-guide.md) | Local, Docker, Vercel, Railway |
| [Docs Index](docs/README.md) | Full documentation map |

See also [docs/architecture.md](docs/architecture.md) and [docs/week7-summary.md](docs/week7-summary.md).

---

## Project Structure

```
mentor-mind-ai/
├── frontend/          # Next.js app
├── backend/           # FastAPI API
├── ml-models/         # Trained model artifacts
├── datasets/          # Raw & processed datasets (gitignored large files)
├── notebooks/         # Jupyter experiments
├── docs/              # Architecture, wireframes, setup guides
└── README.md
```

---

## Installation

### Prerequisites

- Node.js 18+
- Python 3.12+
- PostgreSQL or [Supabase](https://supabase.com) account
- (Optional) Docker

### 1. Clone the repository

```bash
git clone https://github.com/Tharmithan/mentor-mind-ai.git
cd mentor-mind-ai
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # Fill in DATABASE_URL, JWT_SECRET, etc.
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

**Key routes:** `GET /api/health` · `POST /api/predict` (ML) · `GET /api/dashboard` · [Day 7 ML API](docs/day7-ml-api.md)

**Database (Day 5):** See [docs/database-setup.md](docs/database-setup.md) — run `python -m scripts.init_db` and `python -m scripts.seed_db` after Postgres is up.

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local  # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

App: http://localhost:3000

### 4. Database (Supabase)

1. Create a project at [supabase.com](https://supabase.com)
2. Run `docs/database/schema.sql` in the SQL editor
3. Copy connection string into `backend/.env`

---

## Week 1 complete

Professional foundation shipped. See [docs/week1-summary.md](docs/week1-summary.md).

| Area | Delivered |
|------|-----------|
| **Frontend** | Landing page, dashboard (Recharts), responsive UI, AI loading overlay, floating assistant, daily tip |
| **Backend** | FastAPI structure, health/user/predict/recommendations/dashboard/daily-tip |
| **Database** | PostgreSQL schema + SQLite local dev + seed scripts |
| **GitHub** | Documented monorepo, setup guides, clean commits |

---

## Development Roadmap

| Week | Focus | Status |
|------|--------|--------|
| 1 | Setup, architecture, UI, dashboard MVP | ✅ |
| 2 | Data collection, cleaning, EDA, features, training | ✅ |
| 3 | ML models, recommendation engine, AI platform | ✅ |
| 4 | RAG, PDF processing, chat assistant, study tools | ✅ |
| 5 | Mock interview module, STT, emotion detection | ✅ |
| 6 | Multi-agent system, career, resume, coach dashboard | ✅ |
| 7 | Personalization, memory, analytics, MLOps, monitoring, docs | ✅ |
| 8 | Deployment, testing, security, portfolio | 🚧 |

See [docs/week8-day1-deployment.md](docs/week8-day1-deployment.md) for production deploy (Vercel + Railway + Supabase).

---

## Future Improvements

- [ ] Full JWT auth + user registration
- [ ] Multilingual support (English + Tamil)
- [ ] Mobile PWA
- [ ] pgvector migration (ChromaDB → Supabase)
- [ ] Team/classroom admin dashboards

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

## Contributors

Built as a production-quality AI learning platform. Contributions welcome via pull requests.
