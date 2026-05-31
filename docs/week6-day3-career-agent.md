# Week 6 · Day 3 — Career Agent

**Goal:** Help students **choose careers** by analyzing skills, interests, performance, and interview scores — then recommending paths with actionable roadmaps.

---

## Career paths

| Role | Best for students who… |
|------|------------------------|
| **Data Scientist** | Strong in math/statistics, love turning data into insights |
| **AI Engineer** | Strong programmers curious about LLMs, NLP, and applied ML |
| **MLOps Engineer** | Enjoy DevOps, pipelines, and shipping models to production |
| **Software Engineer** | Excel at algorithms, system design, and building products |

---

## Example

```
User: Which career path fits me best?

Career Agent:
  Based on your strengths, Data Scientist is your strongest career path (78% match).

  Performance avg: 68% · Strongest subjects: Programming (78%), Mathematics (58%)

  Why Data Scientist? Match based on academic performance, skill alignment…

  Other paths: AI Engineer — 72% · Software Engineer — 69%
```

---

## Features

### 1. Career recommendation engine
Scores each path using:
- **Subject performance** (Mathematics, Programming, Data Structures…)
- **Derived skills** (statistics, ML, algorithms, communication…)
- **Interview scores** (technical, communication, confidence from mock interviews)
- **Stated interests** (AI, data, software, MLOps keywords)

### 2. Skill gap analysis
Compares your skill levels vs role requirements → prioritized gaps + learning actions.

### 3. Learning roadmap generation
20-week phased roadmaps per career (Foundation → Core → Portfolio/Production).

### 4. Industry trend recommendations
Curated 2025–2026 trends: GenAI, MLOps maturity, responsible AI, AI-assisted dev.

---

## Backend layout

```
backend/app/agents/career/
├── paths.py                  # Career definitions + roadmaps + trends
├── profile_builder.py        # Merge performance + interview + interests
├── recommendation_engine.py  # Score & rank 4 career paths
├── skill_gap.py              # Gap analysis vs target role
├── roadmap_generator.py      # Phased learning roadmaps
├── trends.py                 # Industry trend service
└── service.py                # Orchestration

backend/app/agents/career_agent.py
backend/app/routes/career_agent.py
backend/app/models/career.py
```

---

## API

| Method | Route | Description |
|--------|-------|-------------|
| `POST` | `/api/agents/career/recommend` | Rank career paths |
| `POST` | `/api/agents/career/skill-gaps` | Skill gap analysis |
| `POST` | `/api/agents/career/roadmap` | Learning roadmap |
| `GET` | `/api/agents/career/trends` | Industry trends |
| `POST` | `/api/agents/career/analyze` | Full bundle |

Chat: `POST /api/agents/chat` with career-intent messages routes to Career Agent.

---

## Try it

```bash
# Career recommendation
curl -s -X POST http://127.0.0.1:8000/api/agents/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Which career path fits me best?"}' | jq .answer

# Skill gaps for Data Scientist
curl -s -X POST http://127.0.0.1:8000/api/agents/career/skill-gaps \
  -H "Content-Type: application/json" \
  -d '{"target_career":"data_scientist"}' | jq .summary

# AI Engineer roadmap
curl -s -X POST http://127.0.0.1:8000/api/agents/career/roadmap \
  -H "Content-Type: application/json" \
  -d '{"target_career":"ai_engineer"}' | jq .total_weeks
```

---

## Next (Week 6 · Day 4+)

- Career dashboard panel with match scores chart
- Persist career profile per user account
- LinkedIn/resume alignment suggestions per target role
