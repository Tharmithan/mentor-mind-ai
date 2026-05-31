# Week 8 · Day 1 — Deployment (Vercel + Railway + Supabase)

Deploy MentorMind AI to production: frontend on **Vercel**, backend on **Railway** (or **Render**), database on **Supabase**.

---

## Architecture (Production)

```
Vercel (Next.js)  ──proxy──▶  Railway/Render (FastAPI)  ──▶  Supabase (PostgreSQL)
     │                              │
     └── /api/* rewrites            └── ml-models in Docker image
```

---

## Prerequisites

- [GitHub](https://github.com) repo pushed (13+ commits on `main`)
- [Supabase](https://supabase.com) account (free tier)
- [Vercel](https://vercel.com) account (free tier)
- [Railway](https://railway.app) or [Render](https://render.com) account (free tier)

---

## Step 1 — Supabase Database

### 1.1 Create project

1. Go to [supabase.com/dashboard](https://supabase.com/dashboard) → **New project**
2. Choose region close to your users
3. Save the database password

### 1.2 Run schema

1. Open **SQL Editor** → **New query**
2. Paste contents of [`docs/database/schema.sql`](./database/schema.sql)
3. Click **Run**

### 1.3 Get connection string

1. **Settings** → **Database** → **Connection string** → **URI**
2. Copy the URL and convert for async SQLAlchemy:

```
postgresql+asyncpg://postgres.[PROJECT-REF]:[YOUR-PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```

Use the **Transaction pooler** (port **6543**) for Railway/Render.

> The backend auto-converts `postgres://` → `postgresql+asyncpg://` if you paste the raw Supabase URI.

---

## Step 2 — Backend on Railway

### 2.1 Create project

1. [railway.app/new](https://railway.app/new) → **Deploy from GitHub repo**
2. Select **MentorMindAi** repository
3. Railway detects [`railway.toml`](../railway.toml) and root [`Dockerfile`](../Dockerfile)

### 2.2 Environment variables

In Railway → **Variables**, add:

| Variable | Value |
|----------|-------|
| `DATABASE_URL` | Supabase pooler URL (step 1.3) |
| `JWT_SECRET` | Random string (`openssl rand -hex 32`) |
| `CORS_ORIGINS` | `https://your-app.vercel.app` (update after Vercel deploy) |
| `DEBUG` | `false` |
| `ML_MODELS_DIR` | `/app/ml-models` |
| `AUTO_CREATE_TABLES` | `0` |
| `OPENAI_API_KEY` | Optional — enables LLM features |

Template: [`.env.production.example`](../.env.production.example)

### 2.3 Deploy

1. Railway builds the Docker image (includes `ml-models/` JSON + local joblib if in build context)
2. Copy your public URL: `https://mentormind-api-production.up.railway.app`

### 2.4 Verify

```bash
curl https://YOUR-RAILWAY-URL/api/health
# {"status":"healthy","database":"connected",...}

./scripts/check-deployment.sh https://YOUR-RAILWAY-URL
```

---

## Step 3 — Frontend on Vercel

### 3.1 Import project

1. [vercel.com/new](https://vercel.com/new) → Import GitHub repo
2. **Root Directory:** `frontend` ← important
3. Framework: **Next.js** (auto-detected)

### 3.2 Environment variables

| Variable | Value |
|----------|-------|
| `API_PROXY_URL` | Your Railway backend URL (no trailing slash) |
| `NEXT_PUBLIC_APP_NAME` | `MentorMind AI` |

The Next.js rewrite in [`frontend/next.config.ts`](../frontend/next.config.ts) proxies browser `/api/*` calls to your backend — **no CORS issues**.

### 3.3 Deploy

1. Click **Deploy**
2. Copy URL: `https://mentormind-ai.vercel.app`

### 3.4 Update backend CORS

Go back to Railway → add your Vercel URL to `CORS_ORIGINS`:

```
https://mentormind-ai.vercel.app,https://mentormind-ai-*.vercel.app
```

Redeploy backend if needed.

### 3.5 Verify frontend proxy

```bash
./scripts/check-deployment.sh https://YOUR-RAILWAY-URL https://YOUR-VERCEL-URL
```

Open `https://YOUR-VERCEL-URL/coach` — dashboard should load.

---

## Step 4 — Alternative: Render (Backend)

1. [render.com](https://render.com) → **New** → **Blueprint**
2. Connect repo — uses [`render.yaml`](../render.yaml)
3. Set `DATABASE_URL`, `CORS_ORIGINS`, `JWT_SECRET` in dashboard
4. Deploy

---

## ML Models in Production

Joblib files are gitignored. For full ML inference in production:

**Option A — Build Docker locally (includes models):**
```bash
docker build -f Dockerfile -t mentormind-api .
docker run -p 8000:8000 -e DATABASE_URL=... mentormind-api
```

**Option B — Push models to repo (portfolio):**
```gitignore
# Add to .gitignore exceptions:
!ml-models/saved_models/*.joblib
```

**Option C — Heuristic fallback:** API works without joblib; `/api/ai/status` shows model load state.

---

## Environment Variable Reference

See [`.env.production.example`](../.env.production.example) for the full list.

| Service | Key variables |
|---------|---------------|
| **Supabase** | Connection URI in `DATABASE_URL` |
| **Railway/Render** | `DATABASE_URL`, `JWT_SECRET`, `CORS_ORIGINS`, `DEBUG=false` |
| **Vercel** | `API_PROXY_URL`, `NEXT_PUBLIC_APP_NAME` |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `database: not_connected` | Check Supabase URL, use pooler port 6543, allow IP |
| CORS error in browser | Use Vercel proxy (`API_PROXY_URL`), not direct API URL |
| ML predict returns heuristic | Add joblib to Docker build context |
| 502 on Railway | Check logs; increase health check timeout in `railway.toml` |
| Vercel `/api` 404 | Set `API_PROXY_URL`; redeploy frontend |

---

## Checklist (Day 1 TODO)

- [ ] Supabase project + schema applied
- [ ] Backend deployed on Railway or Render
- [ ] Frontend deployed on Vercel
- [ ] `DATABASE_URL` connected (health shows `connected`)
- [ ] `CORS_ORIGINS` includes Vercel URL
- [ ] `API_PROXY_URL` set on Vercel
- [ ] `./scripts/check-deployment.sh` passes
- [ ] `/coach` dashboard loads in production

---

## Next (Week 8)

| Day | Focus |
|-----|-------|
| 2 | Testing (pytest, API smoke tests) |
| 3 | Security (JWT, rate limits, headers) |
| 4 | Professional GitHub (README, badges, CI) |
| 5 | Portfolio website |
| 6 | Demo video |
| 7 | Resume-ready project summary |

See [week8-summary.md](./week8-summary.md).
