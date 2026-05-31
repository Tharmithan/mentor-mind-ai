# Week 6 · Day 2 — Study Agent (Personal Tutor)

**Goal:** The AI becomes a **personal tutor** — not just answering questions, but creating plans, tracking goals, and recommending what to study each day.

---

## Responsibilities

| Capability | Example user message |
|------------|---------------------|
| **Study plan generator** | _"I have a Machine Learning exam in 14 days"_ |
| **Revision planner** | _"Create a revision plan for Data Structures in 10 days"_ |
| **Learning goal tracker** | _"I want to learn Python in 30 days"_ → _"I completed day 3"_ |
| **Daily study recommendations** | _"What should I study today?"_ |
| **Weak subject analysis** | _"Analyze my weak subjects"_ |

---

## Example flow

```
User: I have a Machine Learning exam in 14 days.

Study Agent:
  → Parses subject + timeline
  → Builds 14-day curriculum (foundations → supervised → NN → exam prep)
  → Returns markdown plan + resource links + dashboard action
```

---

## Backend architecture

```
backend/app/agents/study/
├── curricula.py          # ML / DSA / Programming templates + resource links
├── plan_generator.py     # N-day exam plan (offline + LLM for custom subjects)
├── revision_planner.py     # Phased revision from weak subjects
├── goal_tracker.py         # Goals per agent session → uploads/study_goals/
└── tutor_service.py        # Daily recommendations + weak-subject analysis

backend/app/agents/study_agent.py   # Chat intents wired to tutor services
backend/app/routes/study_agent.py   # REST API
backend/app/models/study_tutor.py   # Pydantic models
```

---

## API

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/agents/study/plan` | Generate exam study plan |
| `POST` | `/api/agents/study/revision` | Revision planner |
| `GET` | `/api/agents/study/daily` | Daily study recommendations |
| `GET` | `/api/agents/study/weak-subjects` | Weak subject analysis |
| `GET` | `/api/agents/study/goals/{session_id}` | List learning goals |
| `POST` | `/api/agents/study/goals/{session_id}` | Create goal |
| `PATCH` | `/api/agents/study/goals/{session_id}/{id}` | Update progress |

Chat routing still works via `POST /api/agents/chat` — the router sends study-intent messages to the Study Agent.

---

## 14-day ML plan (sample)

| Days | Phase | Focus |
|------|-------|-------|
| 1–2 | Foundations | Math refresh, EDA |
| 3–4 | Supervised | Regression & classification |
| 5 | Evaluation | Cross-validation, metrics |
| 6 | Unsupervised | Clustering, PCA |
| 7–8 | Neural Networks | MLPs, CNNs |
| 9–10 | Applied ML | Feature engineering, ensembles |
| 11–12 | Exam prep | Practice problems, mock exam |
| 13–14 | Final review | Light revision, exam readiness |

Each day includes concrete tasks, ~2h duration, and suggested resources (Coursera, scikit-learn, Kaggle, etc.).

---

## Frontend

- `FloatingAIAssistant` quick replies updated for exam plans and weak-subject analysis
- `createExamStudyPlan()`, `getDailyStudyRecommendations()`, `listLearningGoals()` in `lib/api.ts`

---

## Try it

```bash
# 14-day ML exam plan
curl -s -X POST http://127.0.0.1:8000/api/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"I have a Machine Learning exam in 14 days"}' | jq .answer

# Direct plan API
curl -s -X POST http://127.0.0.1:8000/api/agents/study/plan \
  -H "Content-Type: application/json" \
  -d '{"subject":"Machine Learning","days":14}' | jq .schedule[0]

# Daily recommendations
curl -s http://127.0.0.1:8000/api/agents/study/daily | jq .summary
```

Open the floating **MentorMind AI** button → _"I have a Machine Learning exam in 14 days"_.

---

## Next (Week 6 · Day 3+)

- Sync goals with dashboard UI panel
- Calendar export for study plans
- Progress charts tied to ML performance predictions
