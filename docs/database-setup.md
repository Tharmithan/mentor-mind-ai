# Database Setup — Week 1 Day 5

## Stack

- **PostgreSQL** — relational database
- **Supabase** — hosted PostgreSQL (+ auth later)
- **SQLAlchemy 2.0** — Python ORM (async)

---

## Tables (Day 5)

| Table | Purpose | Relationship |
|-------|---------|--------------|
| `users` | Student accounts | Parent |
| `performance_data` | Scores & study metrics | Many per user |
| `interview_results` | Mock interview outcomes | Many per user |
| `recommendations` | AI study suggestions | Many per user |

```
users (1) ──────< performance_data (N)
   │
   ├──────────< interview_results (N)
   │
   └──────────< recommendations (N)
```

---

## Option A — Supabase (recommended)

1. Create a project at [supabase.com](https://supabase.com)
2. Open **SQL Editor** → paste `docs/database/schema.sql` → **Run**
3. Go to **Settings → Database** → copy the connection string (URI)
4. Convert to async format for the backend:

```
postgresql+asyncpg://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres
```

5. Save in `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://...
```

---

## Option B — Local Docker

```bash
# From project root
docker compose up -d db
```

Then:

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mentormind

python -m scripts.init_db
python -m scripts.seed_db
```

---

## SQL basics (quick reference)

```sql
-- Create
CREATE TABLE users (id UUID PRIMARY KEY, email TEXT UNIQUE NOT NULL);

-- Read
SELECT * FROM users WHERE email = 'student@mentormind.ai';

-- Join (relationship)
SELECT u.full_name, p.subject, p.score
FROM users u
JOIN performance_data p ON p.user_id = u.id;

-- Insert
INSERT INTO recommendations (user_id, title, priority)
VALUES ('...', 'Review Algorithms', 'high');
```

---

## ORM (SQLAlchemy)

Python classes map to tables. Example relationship on `User`:

```python
user.performance_data   # list of PerformanceData rows
user.recommendations    # list of Recommendation rows
```

Load with relationships:

```python
select(User).options(selectinload(User.performance_data))
```

---

## Scripts

| Command | Purpose |
|---------|---------|
| `python -m scripts.init_db` | Create tables from ORM |
| `python -m scripts.seed_db` | Insert demo student + sample rows |

---

## API endpoints using the database

| Method | Path | Uses table |
|--------|------|------------|
| GET | `/api/health` | connection check |
| GET | `/api/user` | `users` + `performance_data` |
| POST | `/api/predict` | writes `performance_data` |
| GET | `/api/recommendations` | `recommendations` |

---

## Day 5 checklist

- [x] SQL schema (`docs/database/schema.sql`)
- [x] ORM models with relationships
- [x] `users`, `performance_data`, `interview_results`, `recommendations`
- [x] Init + seed scripts
- [x] API wired to database
