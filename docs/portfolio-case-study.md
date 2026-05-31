# MentorMind AI — Portfolio Case Study

> Full-stack AI learning platform for recruiters, professors, and portfolio reviewers.

---

## Problem

Students struggle to predict academic outcomes, personalize study time, practice interviews, and get career guidance — tools are fragmented across LMS, quiz apps, and generic chatbots.

## Solution

**MentorMind AI** unifies ML performance prediction, RAG-grounded tutoring, mock interviews with feedback, multi-agent career guidance, and an AI Coach dashboard in one deployable platform.

---

## Architecture

```
Next.js (Vercel) → FastAPI (Railway) → AI Services → PostgreSQL + ChromaDB
```

- **Frontend:** Next.js 16, TypeScript, Tailwind, lazy-loaded panels, dark/light mode
- **Backend:** FastAPI, async SQLAlchemy, JWT auth, rate limiting, 70+ endpoints
- **ML:** Random Forest / XGBoost, SHAP explainability, MLOps registry
- **RAG:** PDF upload → chunk → embed → ChromaDB → grounded chat
- **Interview:** Question bank, LLM evaluation, Whisper STT, emotion FER
- **Agents:** Study, Interview, Career, Resume routing

Diagrams: [architecture/](../architecture/) · [docs/architecture.md](./architecture.md)

---

## Key Features Demonstrated

| Capability | Implementation |
|------------|------------------|
| Performance prediction | `POST /api/predict` + SHAP `/predict/explain` |
| Recommendations | Rule + collaborative filtering engine |
| RAG tutor | Document upload + semantic search + chat |
| Interview coach | Session state machine + scoring |
| Personalization | User profiles + embeddings |
| MLOps | Model registry, experiments, promote |
| Monitoring | Feedback loop, drift metrics |
| Admin | User/model overview dashboard |

---

## Engineering Highlights

- **Security:** bcrypt, JWT access/refresh, rate-limited auth, security headers
- **Testing:** 24 pytest tests (unit, integration, e2e) + GitHub Actions CI
- **Performance:** Model warmup, SHAP cache, thread offloading, client-side cache
- **Deployment:** Docker, Vercel, Railway, Supabase configs

---

## Results & Metrics

- ML models: **R² ~0.99** on held-out student performance data
- **24 automated tests** passing in CI
- **8 weeks** structured delivery (UI → ML → RAG → Agents → Production)

---

## Links

| Asset | URL |
|-------|-----|
| GitHub | [github.com/Tharmithan/mentor-mind-ai](https://github.com/Tharmithan/mentor-mind-ai) |
| API Docs | `/docs` (Swagger) |
| Documentation | [docs/README.md](./README.md) |
| Demo GIF | [demo/demo.gif](../demo/demo.gif) |

---

## Resume Bullet Points

Use on CV / LinkedIn:

- Developed a full-stack AI platform using **FastAPI, Next.js, PostgreSQL, PyTorch, and RAG architecture**
- Built **ML models** for performance prediction and recommendation systems with **SHAP explainability**
- Implemented **AI interview coaching** with speech analysis and personalized feedback
- Developed **multi-agent career guidance** and resume analysis modules
- Deployed production-ready application with **JWT authentication, analytics, vector DB, and CI/CD**

---

## Demo Video

Record a 2-minute walkthrough: Dashboard → Predict → Assistant → Interview → Coach.

Add YouTube link to [README](../README.md#demo-video).
