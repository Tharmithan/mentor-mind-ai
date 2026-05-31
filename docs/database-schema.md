# MentorMind AI — Database Schema

> PostgreSQL tables, vector storage, and file-based persistence layers.

---

## 1. Overview

MentorMind uses a **hybrid persistence model**:

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Relational** | PostgreSQL / SQLite | Users, scores, interview results |
| **Vector** | ChromaDB (persistent) | Document embeddings for RAG |
| **File JSON** | `backend/uploads/` | Sessions, profiles, memory, feedback |
| **ML artifacts** | `ml-models/` | joblib models, manifests, MLflow |

The app runs in **demo mode** without Postgres — file stores and mock data fill gaps.

---

## 2. Entity Relationship (PostgreSQL)

```mermaid
erDiagram
    users ||--o{ performance_data : has
    users ||--o{ interview_results : has
    users ||--o{ recommendations : has

    users {
        uuid id PK
        varchar email UK
        varchar password_hash
        varchar full_name
        varchar role
        int xp
        int streak_days
        timestamptz created_at
    }

    performance_data {
        uuid id PK
        uuid user_id FK
        varchar subject
        decimal score
        decimal study_hours
        decimal attendance_pct
        decimal predicted_score
        varchar risk_level
        timestamptz recorded_at
    }

    interview_results {
        uuid id PK
        uuid user_id FK
        varchar mode
        decimal overall_score
        decimal communication_score
        decimal technical_score
        decimal confidence_score
        text feedback_summary
        timestamptz created_at
    }

    recommendations {
        uuid id PK
        uuid user_id FK
        varchar title
        text description
        varchar topic
        varchar priority
        boolean is_completed
        timestamptz created_at
    }
```

---

## 3. PostgreSQL Tables

Full SQL: [database/schema.sql](./database/schema.sql)

### 3.1 `users`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID PK | User identifier |
| `email` | VARCHAR(255) UNIQUE | Login email |
| `password_hash` | VARCHAR(255) | Bcrypt hash |
| `full_name` | VARCHAR(255) | Display name |
| `role` | VARCHAR(50) | `student` or `admin` |
| `xp` | INTEGER | Gamification XP |
| `streak_days` | INTEGER | Study streak |
| `created_at` | TIMESTAMPTZ | Account created |
| `updated_at` | TIMESTAMPTZ | Last update |

### 3.2 `performance_data`

Stores quiz scores and ML prediction outputs.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | UUID FK → users | Owner |
| `subject` | VARCHAR(100) | e.g. Mathematics |
| `score` | DECIMAL(5,2) | Actual score 0–100 |
| `study_hours` | DECIMAL(5,2) | Study hours at record time |
| `attendance_pct` | DECIMAL(5,2) | Attendance % |
| `predicted_score` | DECIMAL(5,2) | ML prediction |
| `risk_level` | VARCHAR(50) | low / medium / high |
| `recorded_at` | TIMESTAMPTZ | Timestamp |

**SQLAlchemy model:** `backend/app/database/models/performance_data.py`

### 3.3 `interview_results`

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | UUID FK | Owner |
| `mode` | VARCHAR(50) | general / technical / behavioral |
| `overall_score` | DECIMAL(3,2) | 0–5 scale |
| `communication_score` | DECIMAL(3,2) | Communication dimension |
| `technical_score` | DECIMAL(3,2) | Technical dimension |
| `confidence_score` | DECIMAL(5,2) | Confidence dimension |
| `feedback_summary` | TEXT | AI summary |

### 3.4 `recommendations`

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | UUID FK | Owner |
| `title` | VARCHAR(255) | Recommendation title |
| `description` | TEXT | Details |
| `topic` | VARCHAR(100) | Subject area |
| `priority` | VARCHAR(20) | low / medium / high |
| `is_completed` | BOOLEAN | Completion flag |

### 3.5 Indexes

```sql
CREATE INDEX idx_performance_data_user ON performance_data(user_id);
CREATE INDEX idx_interview_results_user ON interview_results(user_id);
CREATE INDEX idx_recommendations_user ON recommendations(user_id);
```

---

## 4. Vector Database (ChromaDB)

| Property | Value |
|----------|-------|
| **Path** | `backend/uploads/vectorstore/` |
| **Collection** | `documents` |
| **Distance** | Cosine |
| **Embedding model** | `all-MiniLM-L6-v2` (384-dim) |

**Metadata per chunk:** `document_id`, `filename`, `chunk_index`, `page`

Not stored in PostgreSQL — ChromaDB persists locally. Production can migrate to pgvector on Supabase.

---

## 5. File-Based Stores

| Path | Format | Contents |
|------|--------|----------|
| `uploads/user_profiles/` | JSON | Unified user profiles |
| `uploads/user_embeddings/` | JSON + numpy | Profile embedding vectors |
| `uploads/long_term_memory/` | JSON | Conversations, goals, snapshots |
| `uploads/interview_sessions/` | JSON | Interview session state |
| `uploads/resumes/` | PDF + JSON | Resume uploads and analyses |
| `uploads/documents/` | PDF | RAG source documents |
| `uploads/chat_sessions/` | JSON | Chat conversation history |
| `uploads/agent_sessions/` | JSON | Multi-agent session memory |
| `uploads/monitoring/` | JSON | Feedback + prediction logs |
| `uploads/reports/` | PDF | Generated report files |

---

## 6. ML Artifact Schema

### `best_model.json`

```json
{
  "score_model": "random_forest",
  "score_file": "saved_models/performance_model_v2.joblib",
  "pass_model": "random_forest",
  "pass_file": "saved_models/pass_fail_model_v2.joblib",
  "version": "v2"
}
```

### `model_manifest_v3.json`

```json
{
  "version": "v3",
  "performance_model": "performance_model_v3.joblib",
  "pass_fail_model": "pass_fail_model_v3.joblib",
  "algorithm": "xgboost_tuned",
  "params": { "max_depth": 4, "learning_rate": 0.1095 },
  "trained_at": "2026-05-25T10:45:58+00:00"
}
```

---

## 7. Setup

### Local SQLite (no Docker)

```env
DATABASE_URL=sqlite+aiosqlite:///./mentormind.db
```

```bash
cd backend
python -m app.database.init_db
```

### Docker PostgreSQL + pgvector

```bash
docker compose up -d db
psql postgresql://postgres:postgres@localhost:5432/mentormind -f docs/database/schema.sql
```

### Supabase

1. Create project at [supabase.com](https://supabase.com)
2. Run `docs/database/schema.sql` in SQL Editor
3. Set `DATABASE_URL=postgresql+asyncpg://...` in `.env`

See [database-setup.md](./database-setup.md).

---

## 8. Future Schema Extensions

| Table | Purpose |
|-------|---------|
| `document_chunks` | pgvector-native RAG (migrate from ChromaDB) |
| `study_plans` | Persisted learning plans |
| `feedback_events` | Move monitoring JSON to Postgres |
| `model_predictions` | Audit trail for ML inference |
