# MentorMind AI — Development Setup

## Quick start (local)

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```
→ http://localhost:3000

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```
→ http://localhost:8000/docs

### Database (choose one)

**Option A — Docker (local PostgreSQL + pgvector)**
```bash
docker compose up -d db
# Apply schema after DB is ready:
psql postgresql://postgres:postgres@localhost:5432/mentormind -f docs/database/schema.sql
```

**Option B — Supabase (recommended for production)**
1. Create project at https://supabase.com
2. SQL Editor → paste `docs/database/schema.sql`
3. Settings → Database → copy connection string
4. Set `DATABASE_URL` in `backend/.env` (use `postgresql+asyncpg://...`)

---

## GitHub repository

Repo name: **mentor-mind-ai**

```bash
# From project root (after removing nested frontend .git if present)
rm -rf frontend/.git
git init
git add .
git commit -m "feat: Week 1 foundation — MentorMind AI monorepo"

# Create repo on GitHub (CLI or web UI), then:
git remote add origin https://github.com/Tharmithan/mentor-mind-ai.git
git branch -M main
git push -u origin main
```

---

## Week 1 checklist

- [x] Project name: MentorMind AI
- [x] Folder structure
- [x] README & architecture docs
- [x] UI design doc & wireframes
- [x] Next.js frontend + homepage + dashboard
- [x] FastAPI backend scaffold
- [x] PostgreSQL schema (Supabase-ready)
- [ ] GitHub remote push (requires your GitHub account)
