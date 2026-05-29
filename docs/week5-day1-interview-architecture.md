# Week 5 · Day 1 — Interview System Architecture

**Goal:** Design the complete **AI Interview Coach** workflow — the feature that can
become the best part of MentorMind.

---

## Interview flow

```
User starts interview (pick type: HR / Technical / Behavioral)
        ↓
AI asks question (from question database)
        ↓
User answers (text today · voice Day 2+)
        ↓
Speech-to-text                    ← planned Day 2
        ↓
AI analyzes answer                ← heuristic scorer (Day 1); LLM later
        ↓
Score generated (overall + dimensions)
        ↓
Feedback shown → next question … → final summary
```

---

## Interview types

| Type | Focus | Example questions |
|------|--------|-------------------|
| **HR** | Introduction, motivation, fit | Tell me about yourself; strengths/weaknesses |
| **Technical** | DSA, AI/ML, web dev | Stacks vs queues; REST APIs; embeddings |
| **Behavioral** | STAR stories | Teamwork; leadership; conflict |

Question bank: `backend/app/interview/data/questions.json` (6–7 questions per type).

---

## Backend architecture

```
backend/app/interview/
├── data/questions.json      # question database
├── types.py                 # HR | technical | behavioral
├── question_bank.py         # load + random pick
├── analyzer.py              # score + feedback (Day 1 heuristic)
├── session.py               # session state machine + JSON persistence
└── service.py               # API orchestration

backend/app/routes/interview.py
backend/app/models/interview.py
```

Sessions persist to `backend/uploads/interview_sessions/` (gitignored).

### API

| Method | Route | Description |
|--------|-------|-------------|
| `GET` | `/api/interview/types` | List interview types + question counts |
| `POST` | `/api/interview/start` | `{ interview_type, num_questions }` → session + Q1 |
| `GET` | `/api/interview/session/{id}` | Full session state |
| `POST` | `/api/interview/session/{id}/answer` | Submit answer → scores + feedback + next Q |

### Scoring (Day 1)

Heuristic dimensions (0–10): length, structure, relevance, clarity → overall score.
Behavioral answers bonus for STAR-style markers. Day 2+ can plug in LLM evaluation.

---

## Frontend

| Component | Role |
|-----------|------|
| `InterviewSetup` | Choose HR / Technical / Behavioral |
| `InterviewCoach` | Full flow: question → analyzing → feedback → complete |
| `/interview` | Page shell |

UI phases: **setup** → **question** → **analyzing** → **feedback** → **complete**

Optional webcam + mic toggles (mic → speech-to-text in Day 2).

---

## Database (existing)

`InterviewResult` ORM model is ready for persisting final scores to Postgres when auth
is wired. Day 1 uses JSON session files for speed.

---

## Checklist

- [x] Create interview flow (session state machine + API)
- [x] Create question database (HR, technical, behavioral)
- [x] Design interview UI (type picker + live interview room)

---

## Next (Day 2)

Speech-to-text, LLM answer analysis, and saving results to the database.
