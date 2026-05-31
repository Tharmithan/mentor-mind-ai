# Week 8 — Deployment, Testing, Security & Portfolio

> Turn MentorMind AI into something you can confidently show recruiters, professors, and interviewers.

---

## Week 8 Goal

By end of Week 8:

- ✅ Fully deployed application
- ✅ Production-ready APIs
- ✅ Testing completed
- ✅ Security improvements
- ✅ Professional GitHub
- ✅ Portfolio website
- ✅ Demo video
- ✅ Resume-ready project

---

## Days

| Day | Focus | Doc |
|-----|-------|-----|
| **1** | Deployment (Vercel + Railway + Supabase) | [week8-day1-deployment.md](./week8-day1-deployment.md) |
| **2** | Security (JWT, refresh tokens, rate limiting) | [week8-day2-security.md](./week8-day2-security.md) |
| **3** | Testing (unit, integration, e2e) | [week8-day3-testing.md](./week8-day3-testing.md) |
| **4** | Performance optimization | [week8-day4-performance.md](./week8-day4-performance.md) |
| **5** | Professional documentation | [week8-day5-documentation.md](./week8-day5-documentation.md) |
| **6** | GitHub optimization | [week8-day6-github-optimization.md](./week8-day6-github-optimization.md) |
| 7 | Portfolio website | _coming soon_ |
| 8 | Demo video | _coming soon_ |
| 9 | Resume-ready summary | _coming soon_ |

---

## Production Stack

| Layer | Platform |
|-------|----------|
| Frontend | [Vercel](https://vercel.com) |
| Backend | [Railway](https://railway.app) or [Render](https://render.com) |
| Database | [Supabase](https://supabase.com) |

---

## Quick Deploy

```bash
# 1. Supabase — run docs/database/schema.sql

# 2. Railway — connect GitHub repo, set env vars from .env.production.example

# 3. Vercel — root directory: frontend, set API_PROXY_URL

# 4. Verify
chmod +x scripts/check-deployment.sh
./scripts/check-deployment.sh https://YOUR-API.railway.app https://YOUR-APP.vercel.app
```

---

## Config Files Added (Day 1)

| File | Purpose |
|------|---------|
| `Dockerfile` | Production backend image (repo root) |
| `railway.toml` | Railway deploy config |
| `render.yaml` | Render blueprint |
| `frontend/vercel.json` | Vercel settings |
| `.env.production.example` | Production env template |
| `scripts/check-deployment.sh` | Post-deploy smoke test |
