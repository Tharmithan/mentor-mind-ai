# MentorMind AI — Deployment Guide

> Local development → Docker → cloud production (Vercel + Railway + Supabase)

---

## 1. Prerequisites

| Tool | Version |
|------|---------|
| Node.js | 18+ |
| Python | 3.12+ |
| Docker | 24+ (optional) |
| Git | 2.x |

---

## 2. Local Development (Recommended)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Optional feature packs
pip install -r requirements-rag.txt       # RAG + embeddings
pip install -r requirements-interview.txt # STT + emotion
pip install -r requirements-reports.txt   # PDF reports
pip install -r requirements-mlops.txt     # MLflow

cp .env.example .env
# Edit: DATABASE_URL, OPENAI_API_KEY (optional)

uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000  
- Docs: http://localhost:8000/docs  

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev
```

- App: http://localhost:3000  

### Database (optional)

**SQLite (zero setup):**
```env
DATABASE_URL=sqlite+aiosqlite:///./mentormind.db
```

**PostgreSQL via Docker:**
```bash
docker compose up -d db
psql postgresql://postgres:postgres@localhost:5432/mentormind -f docs/database/schema.sql
```

---

## 3. Docker Compose (Full Stack)

### Standard stack (API + Postgres)

```bash
docker compose up --build
```

| Service | Port | Description |
|---------|------|-------------|
| `backend` | 8000 | FastAPI API |
| `db` | 5432 | PostgreSQL + pgvector |

### MLOps stack (API + MLflow)

```bash
docker compose -f docker-compose.mlops.yml up --build
```

| Service | Port | Description |
|---------|------|-------------|
| `mlflow` | 5000 | Experiment tracking UI |
| `api` | 8000 | API with `ml-models` volume |

**Important:** Mount `ml-models/` so inference artifacts are available:

```yaml
volumes:
  - ./ml-models:/app/ml-models
```

### Backend Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Production tip: copy `ml-models/` into the image or mount as volume.

---

## 4. Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | No* | Postgres or SQLite async URL |
| `JWT_SECRET` | Prod | Random secret string |
| `CORS_ORIGINS` | Yes | Frontend URL(s) |
| `OPENAI_API_KEY` | No | Enables LLM features |
| `OPENAI_MODEL` | No | Default: gpt-4o-mini |
| `MLFLOW_TRACKING_URI` | No | MLflow server or file URI |
| `SMTP_*` | No | Email reports (Week 7 Day 4) |
| `MLOPS_RUN_TRAINING` | No | Set `1` to trigger retrain via API |

\*App works without DB in demo mode.

### Frontend (`frontend/.env.local`)

| Variable | Description |
|----------|-------------|
| `NEXT_PUBLIC_API_URL` | Backend URL (e.g. `https://api.example.com`) |

---

## 5. Cloud Deployment

### Recommended topology

| Component | Platform | Notes |
|-----------|----------|-------|
| **Frontend** | [Vercel](https://vercel.com) | Connect GitHub repo, set root to `frontend/` |
| **Backend** | [Railway](https://railway.app) | Docker or Nixpacks, set start command |
| **Database** | [Supabase](https://supabase.com) | Managed Postgres + pgvector |
| **ML artifacts** | Railway volume or S3 | Mount `ml-models/` |

### Vercel (Frontend)

1. Import repository
2. **Root Directory:** `frontend`
3. **Build Command:** `npm run build`
4. **Environment:** `NEXT_PUBLIC_API_URL=https://your-api.railway.app`
5. Deploy

### Railway (Backend)

1. New project → Deploy from GitHub
2. **Root Directory:** `backend`
3. **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `.env.example`
5. Add volume for `uploads/` and `ml-models/` (or bake models into image)

### Supabase (Database)

1. Create project
2. SQL Editor → run `docs/database/schema.sql`
3. Copy connection string → set `DATABASE_URL`:
   ```
   postgresql+asyncpg://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```

---

## 6. Production Checklist

- [ ] Set strong `JWT_SECRET`
- [ ] Restrict `CORS_ORIGINS` to production frontend URL
- [ ] Enable HTTPS (automatic on Vercel/Railway)
- [ ] Copy `ml-models/saved_models/*.joblib` to server (or use MLOps promote)
- [ ] Set `OPENAI_API_KEY` if LLM features needed
- [ ] Configure SMTP for email reports (optional)
- [ ] Run `docs/database/schema.sql` on production Postgres
- [ ] Set up health check: `GET /api/health`
- [ ] Enable MLflow tracking for experiment audit (optional)

---

## 7. CI/CD (Suggested)

```yaml
# .github/workflows/ci.yml (example)
name: CI
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r backend/requirements.txt
      - run: cd backend && python -c "from app.main import app"
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd frontend && npm ci && npm run build
```

---

## 8. Monitoring in Production

| Endpoint | Purpose |
|----------|---------|
| `GET /api/health` | Uptime check |
| `GET /api/mlops/status` | Model pipeline health |
| `GET /api/monitoring/model-metrics` | Prediction drift |
| `GET /api/ai/status` | ML model loaded? |

---

## 9. Troubleshooting

| Issue | Fix |
|-------|-----|
| CORS errors | Add frontend URL to `CORS_ORIGINS` |
| ML predict fails | Ensure `ml-models/best_model.json` + joblib files exist |
| RAG empty | Install `requirements-rag.txt`, upload a PDF |
| LLM unavailable | Set `OPENAI_API_KEY` or use heuristic fallbacks |
| DB connection fails | Check `DATABASE_URL` format (`+asyncpg` for Postgres) |
| ChromaDB errors | Delete `uploads/vectorstore/` and re-index |

---

## 10. Related Docs

- [Architecture](./architecture.md)
- [API Reference](./api-reference.md)
- [Database Schema](./database-schema.md)
- [Setup](./setup.md)
