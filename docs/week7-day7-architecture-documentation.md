# Week 7 · Day 7 — Architecture & Documentation

Make the project look **industry-level** with complete architecture diagrams and production documentation.

---

## Deliverables

| Item | Location |
|------|----------|
| **System architecture diagram** | [diagrams/system-architecture.mmd](./diagrams/system-architecture.mmd) |
| **Architecture guide** | [architecture.md](./architecture.md) |
| **API reference** | [api-reference.md](./api-reference.md) |
| **AI models catalog** | [ai-models.md](./ai-models.md) |
| **Database schema** | [database-schema.md](./database-schema.md) |
| **Deployment guide** | [deployment-guide.md](./deployment-guide.md) |
| **Documentation index** | [README.md](./README.md) |

---

## System Architecture (Layered)

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

This matches how production AI platforms are structured — clear layers, optional dependencies, and hybrid persistence.

---

## Documentation Map

### For recruiters / portfolio reviewers

Start here:
1. [architecture.md](./architecture.md) — high-level design + data flows
2. [ai-models.md](./ai-models.md) — ML, LLM, agents
3. [api-reference.md](./api-reference.md) — 70+ endpoints

### For developers

1. [setup.md](./setup.md) — quick local start
2. [database-schema.md](./database-schema.md) — tables + file stores
3. [deployment-guide.md](./deployment-guide.md) — Docker → cloud

### Week 7 feature docs

| Day | Doc |
|-----|-----|
| 1 | [user-personalization-engine](./week7-day1-user-personalization-engine.md) |
| 2 | [long-term-memory](./week7-day2-long-term-memory.md) |
| 3 | [learning-analytics](./week7-day3-ai-learning-analytics.md) |
| 4 | [automated-reports](./week7-day4-automated-report-generator.md) |
| 5 | [mlops-pipeline](./week7-day5-mlops-pipeline.md) |
| 6 | [monitoring-feedback](./week7-day6-monitoring-feedback.md) |
| 7 | This document |

---

## Key Architecture Highlights

### Modular monolith
Single FastAPI deployable with 20+ domain packages — not microservices overhead, but clean boundaries.

### Hybrid persistence
- **PostgreSQL** — users, scores (when configured)
- **ChromaDB** — document vectors
- **JSON files** — sessions, memory, feedback (works offline)

### Graceful degradation
OpenAI, MLflow, SMTP, Postgres all optional — demo works out of the box.

### Production patterns
- OpenAPI auto-docs
- Model versioning + promotion (MLOps)
- Feedback loop → recommendation adjustment
- Docker Compose for local + MLOps stack

---

## View the Diagram

**Mermaid file:** [diagrams/system-architecture.mmd](./diagrams/system-architecture.mmd)

Paste into [mermaid.live](https://mermaid.live) or render in GitHub/GitLab markdown.

---

## Week 7 Complete

| Day | Feature | Status |
|-----|---------|--------|
| 1 | User personalization engine | ✅ |
| 2 | Long-term memory | ✅ |
| 3 | Learning analytics | ✅ |
| 4 | Automated reports (PDF/email) | ✅ |
| 5 | MLOps pipeline | ✅ |
| 6 | Monitoring & feedback loop | ✅ |
| 7 | Architecture & documentation | ✅ |

---

## Next: Portfolio Presentation

When presenting to recruiters:

1. Show **architecture diagram** — layered, not spaghetti
2. Walk through **one API flow** (predict → monitor → feedback → improve)
3. Highlight **MLOps** (version, experiment, promote)
4. Demo **Coach dashboard** — single pane for all Week 7 features
5. Point to **deployment guide** — you know how to ship it
