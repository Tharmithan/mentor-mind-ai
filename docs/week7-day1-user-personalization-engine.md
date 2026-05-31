# Week 7 · Day 1 — User Personalization Engine

**Goal:** Every user gets unique recommendations based on weak/strong subjects, learning style, interview history, and career goals.

---

## Example

**User A** (video learner):
- AI recommends YouTube tutorials, video lectures, interactive courses

**User B** (reading learner):
- AI recommends PDFs, official documentation, structured notes

---

## Architecture

```
Performance data + Interview sessions + Preferences
              ↓
      UserProfileEngine
              ↓
    UnifiedUserProfile (JSON store)
              ↓
    UserEmbeddingService → user_embeddings/
              ↓
    PersonalizedRecommender → style-filtered resources
```

---

## Backend layout

```
backend/app/personalization/
├── profile_engine.py    # Build unified profile from DB + files
├── preferences.py       # Learning style tracking & inference
├── embeddings.py        # User vectors (SentenceTransformers + fallback)
├── recommender.py       # Style-aware resource recommendations
└── store.py             # uploads/user_profiles/ + user_embeddings/
```

---

## What the AI learns

| Signal | Source |
|--------|--------|
| Weak subjects | `subject_scores` < 70% |
| Strong subjects | `subject_scores` ≥ 80% |
| Learning style | Explicit preference or inferred |
| Interview history | `uploads/interview_sessions/` |
| Career goals | Profile `career_goal` + interests |

---

## API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/personalization/profile/{user_id}` | Unified profile |
| POST | `/api/personalization/profile/build` | Rebuild + refresh embedding |
| PATCH | `/api/personalization/profile/{user_id}` | Update goals/scores |
| PATCH | `/api/personalization/preferences/{user_id}` | Set learning style |
| GET | `/api/personalization/recommendations/{user_id}` | Personalized resources |
| GET | `/api/personalization/similar/{user_id}` | Similar users by embedding |

---

## Learning styles

| Style | Default formats |
|-------|-----------------|
| `video` | YouTube tutorials, video lectures |
| `reading` | PDFs, documentation, notes |
| `interactive` | Quizzes, flashcards, LeetCode |
| `hands_on` | Projects, GitHub repos, Kaggle |

---

## Integration

- **Study Agent** `GET /api/agents/study/daily?user_id=` merges personalized resources
- **AI Coach** `/coach` — PersonalizationPanel with style picker
- Reuses `ProfileBuilder`, `LEARNING_RESOURCES`, RAG `Embedder`

---

## Smoke test

```bash
cd backend
python -c "
import asyncio
from app.personalization.profile_engine import UserProfileEngine
from app.personalization.recommender import PersonalizedRecommender

async def main():
    p = await UserProfileEngine.get_or_build('demo-user-001')
    r = PersonalizedRecommender.recommend(p)
    print('style:', r.learning_style)
    print('resources:', len(r.resources))

asyncio.run(main())
"
```

Switch learning style on `/coach` → recommendations update instantly.
