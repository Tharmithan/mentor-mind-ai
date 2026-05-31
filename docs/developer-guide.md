# MentorMind AI — Developer Guide

> Onboarding for contributors — repo structure, local setup, testing, and conventions.

---

## Repository Structure

```
MentorMindAi/
├── frontend/           # Next.js 16 app
│   └── src/
│       ├── app/        # App Router pages
│       ├── components/ # UI components by feature
│       └── lib/        # api.ts, types, queryCache
├── backend/
│   └── app/
│       ├── main.py     # FastAPI entry + routers
│       ├── routes/     # HTTP controllers
│       ├── services/   # Business logic
│       ├── ai/         # ML predictor, SHAP, insights
│       ├── rag/        # Document service, vector store, LLM
│       ├── interview/  # Session, evaluator, STT, FER
│       ├── agents/     # Multi-agent router
│       ├── auth/       # JWT, passwords, refresh tokens
│       └── database/   # SQLAlchemy models + session
├── ml-models/          # joblib artifacts + best_model.json
├── datasets/           # Training data + scripts
├── docs/               # All documentation
├── scripts/            # deploy, test, benchmark helpers
└── .github/workflows/  # CI (pytest)
```

---

## Local Development

### Prerequisites

- Python 3.12+, Node.js 18+, Git
- Optional: Docker, PostgreSQL, OpenAI API key

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-test.txt   # for pytest

cp .env.example .env
# Minimum: JWT_SECRET, DATABASE_URL (or omit for demo mode)

uvicorn app.main:app --reload --port 8000
```

**Optional feature packs:**

```bash
pip install -r requirements-rag.txt        # embeddings + ChromaDB
pip install -r requirements-interview.txt # Whisper + OpenCV
pip install -r requirements-mlops.txt     # MLflow
pip install -r requirements-reports.txt     # PDF reports
```

### Frontend

```bash
cd frontend
npm install
npm run dev    # http://localhost:3000
```

API calls proxy through Next.js rewrites (`/api/*` → backend).

### Database

**SQLite (zero config):**
```env
DATABASE_URL=sqlite+aiosqlite:///./mentormind.db
AUTO_CREATE_TABLES=true
```

**PostgreSQL / Supabase:**
```bash
psql $DATABASE_URL -f docs/database/schema.sql
```

---

## Running Tests

```bash
cd backend
pytest -v

# Or from repo root
./scripts/run-tests.sh
```

Test layout:
- `tests/unit/` — passwords, JWT
- `tests/integration/` — auth, AI, RAG, interview, DB
- `tests/e2e/` — cross-module flows

Fixtures use in-memory SQLite and disable rate limiting.

---

## Adding a New API Endpoint

1. **Model** — `backend/app/models/your_feature.py` (Pydantic)
2. **Service** — `backend/app/services/` or domain module
3. **Route** — `backend/app/routes/your_feature.py`
4. **Register** — `app.include_router(...)` in `main.py`
5. **Frontend** — add function in `frontend/src/lib/api.ts` + types
6. **Test** — `backend/tests/integration/test_your_feature.py`
7. **Docs** — update `docs/api-reference.md`

### Conventions

- Routes prefixed with `/api` unless legacy root aliases (`/predict`)
- CPU-bound work: `await asyncio.to_thread(...)` (see Week 8 performance)
- Auth-protected routes: `Depends(get_current_user_required)`
- Rate-limited auth: `@limiter.limit` **before** `@router.post`

---

## AI / ML Development

| Component | Location | Notes |
|-----------|----------|-------|
| Predictor | `app/ai/predictor.py` | Loads from `ML_MODELS_DIR` or `ml-models/` |
| SHAP | `app/ai/explainer.py` | TreeExplainer cached per model |
| RAG | `app/rag/` | Upload → chunk → embed → Chroma → chat |
| Interview | `app/interview/` | In-memory sessions + disk persist |
| Agents | `app/agents/` | Keyword router → handler per agent type |

Retrain models:
```bash
cd datasets/scripts
python train_models.py   # writes to ml-models/
```

---

## Environment Variables

See `backend/.env.example` and `.env.production.example`.

| Variable | Required | Purpose |
|----------|----------|---------|
| `JWT_SECRET` | Production | Sign access/refresh tokens |
| `DATABASE_URL` | Optional | Postgres/SQLite; omit for demo |
| `OPENAI_API_KEY` | Optional | LLM chat, interview eval, reports |
| `ML_MODELS_DIR` | Optional | Override model path in production |
| `CORS_ORIGINS` | Production | Frontend URL(s) |
| `AUTH_RATE_LIMIT_PER_MINUTE` | Optional | Login/register throttle |

---

## Deployment

Full guide: [deployment-guide.md](./deployment-guide.md)

```bash
# Smoke test after deploy
./scripts/check-deployment.sh https://YOUR-API.railway.app https://YOUR-APP.vercel.app

# Benchmark latency
./scripts/benchmark-api.sh https://YOUR-API.railway.app
```

---

## Code Style

- **Python:** Match existing module patterns; type hints on public functions
- **TypeScript:** `"use client"` only when needed; dynamic import heavy panels
- **Commits:** `feat(week8): Day N — short description`
- **Docs:** Update `docs/README.md` index when adding major features

---

## Useful Commands

```bash
# OpenAPI docs
open http://localhost:8000/docs

# Latency metrics
curl http://localhost:8000/api/metrics/latency

# Health check
curl http://localhost:8000/api/health

# Frontend production build
cd frontend && npm run build
```

---

## Getting Help

- Architecture: [architecture.md](./architecture.md)
- API list: [api-reference.md](./api-reference.md)
- Week-by-week feature docs: [README.md](./README.md)
