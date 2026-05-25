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

## Option B — Local SQLite (fastest, no Docker)

Already configured in `backend/.env` for quick dev:

```env
DATABASE_URL=sqlite+aiosqlite:///./mentormind.db
```

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
python -m scripts.init_db
python -m scripts.seed_db
uvicorn app.main:app --reload --port 8000
```

Use **PostgreSQL/Supabase** for production (see options A and C below).

---

## Option C — Local Docker

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

## Troubleshooting

### `password authentication failed for user "postgres"`

Your `.env` password does not match the running Postgres server.

- **Docker Compose** (password must be `postgres`):
  ```bash
  # Start Docker Desktop first, then:
  docker compose up -d db
  ```
  Use in `backend/.env`:
  ```
  DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/mentormind
  ```

- **Another Postgres on port 5432?** Either stop it, or set `DATABASE_URL` to that server's user/password.

Check connection:
```bash
cd backend && python -m scripts.check_db
```

### `Cannot connect to the Docker daemon`

Open **Docker Desktop** and wait until it says "Running", then run `docker compose up -d db` again.

### API returns 500 on `/api/recommendations`

Fixed: API now falls back to **mock data** when the database is unavailable. Connect the DB to persist real data.

---

## Day 5 checklist

- [x] SQL schema (`docs/database/schema.sql`)
- [x] ORM models with relationships
- [x] `users`, `performance_data`, `interview_results`, `recommendations`
- [x] Init + seed scripts
- [x] API wired to database (with mock fallback when offline)
