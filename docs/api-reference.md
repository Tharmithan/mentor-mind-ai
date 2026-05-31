# MentorMind AI — API Reference

> Base URL: `http://localhost:8000` · OpenAPI: `/docs` · Prefix: `/api` (unless noted)

All endpoints return JSON. Authentication is optional in demo mode (`demo-user-001`).

---

## Health & User

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Service health check |
| GET | `/api/user` | Demo user profile |

---

## AI Platform (ML + Analytics)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/predict` | Student performance prediction |
| POST | `/predict` | Same (root alias) |
| POST | `/api/predict/explain` | Prediction + SHAP explainability |
| POST | `/api/recommend` | Study recommendations |
| GET | `/api/analytics` | Dashboard analytics |
| GET | `/api/insights` | AI-generated insights |
| GET | `/api/ai/status` | ML model load status |
| GET | `/api/explain/global` | Global feature importance |

---

## Dashboard & Coach

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/dashboard` | Main dashboard metrics |
| GET | `/api/coach/overview` | AI Coach score cards, charts, skill gaps |
| GET | `/api/coach/weekly-report` | Weekly progress report |
| GET | `/api/recommendations` | General study recommendations |
| GET | `/api/daily-tip` | Daily AI study tip |
| POST | `/api/study-planner` | Generate daily study plan |
| GET | `/api/study-planner` | Get study plan |

---

## Personalization (Week 7)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/personalization/profile/{user_id}` | Unified user profile |
| POST | `/api/personalization/profile/build` | Rebuild profile + embedding |
| PATCH | `/api/personalization/profile/{user_id}` | Update scores, goals |
| PATCH | `/api/personalization/preferences/{user_id}` | Learning style preferences |
| GET | `/api/personalization/recommendations/{user_id}` | Style-aware recommendations |
| GET | `/api/personalization/similar/{user_id}` | Similar users by embedding |

---

## Long-Term Memory (Week 7)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/memory/{user_id}` | Full memory record |
| GET | `/api/memory/{user_id}/context` | Context for agents |
| GET | `/api/memory/{user_id}/progress` | Month-over-month progress |
| GET | `/api/memory/demo/progress` | Demo progress |
| POST | `/api/memory/{user_id}/sync` | Sync from chat/interview stores |
| POST | `/api/memory/{user_id}/snapshot` | Record subject score |
| POST | `/api/memory/{user_id}/career-goal` | Record career goal |

---

## Learning Analytics & Reports (Week 7)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/learning-analytics/demo` | Demo analytics dashboard |
| GET | `/api/learning-analytics/{user_id}` | User learning analytics |
| GET | `/api/reports/weekly/{user_id}` | Weekly report (JSON + markdown) |
| GET | `/api/reports/monthly/{user_id}` | Monthly report |
| POST | `/api/reports/weekly/{user_id}/pdf` | Download weekly PDF |
| POST | `/api/reports/monthly/{user_id}/pdf` | Download monthly PDF |
| POST | `/api/reports/weekly/{user_id}/email` | Email weekly report |
| POST | `/api/reports/monthly/{user_id}/email` | Email monthly report |

---

## MLOps (Week 7)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/mlops/status` | Pipeline health |
| GET | `/api/mlops/models` | Model version registry |
| GET | `/api/mlops/experiments` | Experiment runs |
| GET | `/api/mlops/experiments/compare` | Compare versions (`?versions=v2,v3`) |
| POST | `/api/mlops/experiments/run` | Log or run training experiment |
| POST | `/api/mlops/models/promote` | Deploy version to production |
| GET | `/api/mlops/deployments` | Deployment history |
| GET | `/api/mlops/docker` | Docker commands |

---

## Monitoring & Feedback (Week 7)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/monitoring/feedback` | Submit rating / comment |
| GET | `/api/monitoring/feedback/{user_id}` | User feedback history |
| GET | `/api/monitoring/satisfaction/{user_id}` | Satisfaction summary |
| GET | `/api/monitoring/model-metrics` | Prediction MAE, drift |
| GET | `/api/monitoring/improvements/{user_id}` | Improvement loop insights |
| GET | `/api/monitoring/dashboard/{user_id}` | Full monitoring dashboard |
| GET | `/api/monitoring/demo` | Demo dashboard |

### Example: Submit feedback

```bash
curl -X POST http://localhost:8000/api/monitoring/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "demo-user-001",
    "category": "recommendation",
    "target_id": "LeetCode Arrays",
    "rating": 1,
    "helpful": false,
    "comment": "Recommendation was not useful"
  }'
```

### Example: Predict

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"study_hours": 5, "attendance": 82, "sleep_hours": 7}'
```

---

## Multi-Agent System (Week 6)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/agents/types` | Available agents |
| POST | `/api/agents/chat` | Chat with routed agent |
| POST | `/api/agents/collaborate` | Multi-agent collaboration |
| GET | `/api/agents/session/{session_id}` | Session history |

### Study Agent

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/agents/study/plan` | Exam study plan |
| POST | `/api/agents/study/revision` | Revision plan |
| GET | `/api/agents/study/daily` | Daily recommendations |
| GET | `/api/agents/study/weak-subjects` | Weak subject analysis |
| GET | `/api/agents/study/goals/{session_id}` | List goals |
| POST | `/api/agents/study/goals/{session_id}` | Create goal |
| PATCH | `/api/agents/study/goals/{session_id}/{goal_id}` | Update goal |

### Career Agent

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/agents/career/recommend` | Career recommendation |
| POST | `/api/agents/career/skill-gaps` | Skill gap analysis |
| POST | `/api/agents/career/roadmap` | Learning roadmap |
| GET | `/api/agents/career/trends` | Industry trends |
| POST | `/api/agents/career/analyze` | Full career analysis |

---

## Interview Coach (Week 5)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/interview/types` | Interview types (HR, technical, behavioral) |
| POST | `/api/interview/start` | Start session |
| GET | `/api/interview/session/{session_id}` | Session state |
| POST | `/api/interview/session/{session_id}/answer` | Submit answer + get feedback |
| GET | `/api/interview/session/{session_id}/coach` | Post-session coach report |
| POST | `/api/interview/transcribe` | Speech-to-text |
| POST | `/api/interview/emotion/analyze` | Facial emotion analysis |

---

## RAG & Documents (Week 4)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/documents/upload` | Upload PDF |
| GET | `/api/documents` | List documents |
| POST | `/api/documents/search` | Semantic search |
| POST | `/api/documents/chat` | RAG Q&A over documents |
| GET | `/api/documents/{document_id}/chunks` | View chunks |
| DELETE | `/api/documents/{document_id}` | Delete document |

---

## Study Tools (Week 4)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/study/status` | LLM availability |
| POST | `/api/study/summarize` | Summarize document |
| POST | `/api/study/quiz` | Generate quiz |
| POST | `/api/study/flashcards` | Generate flashcards |
| POST | `/api/study/explain` | Explain concept simply |
| POST | `/api/study/revision` | Revision plan |

---

## Chat Sessions (Week 4)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/chat/sessions` | Create session |
| GET | `/api/chat/sessions/{session_id}` | Get session |
| DELETE | `/api/chat/sessions/{session_id}` | Delete session |

---

## Resume Analyzer (Week 6)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/resume/upload` | Upload PDF resume |
| POST | `/api/resume/analyze` | Analyze text |
| GET | `/api/resume/analysis/{analysis_id}` | Get analysis result |

---

## Learning Planner (Week 6)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/learning-planner/roadmap` | Generate roadmap |
| POST | `/api/learning-planner/plans` | Create plan |
| GET | `/api/learning-planner/plans/{plan_id}` | Get plan |
| PATCH | `/api/learning-planner/plans/{plan_id}/progress` | Update progress |
| GET | `/api/learning-planner/plans/{plan_id}/weekly` | Weekly breakdown |

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 404 | Resource not found |
| 422 | Validation error |
| 500 | Server error |

Interactive docs: **http://localhost:8000/docs**
