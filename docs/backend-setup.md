# Backend Setup — Week 1 Day 4

## Stack

- **FastAPI** — REST API
- **Uvicorn** — ASGI server
- **SQLAlchemy + asyncpg** — PostgreSQL (Supabase-ready)
- **Pydantic** — Request/response validation

## Project structure

```
backend/
├── app/
│   ├── routes/          # API endpoints
│   │   ├── health.py    # GET /api/health
│   │   ├── user.py      # GET /api/user
│   │   └── predict.py   # POST /api/predict
│   ├── models/          # Pydantic schemas
│   ├── services/        # Business logic
│   ├── database/        # DB session & connection
│   ├── config.py
│   └── main.py
├── requirements.txt
├── .env.example
└── Dockerfile
```

## API routes

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Service + DB status |
| GET | `/api/user` | Demo user profile |
| POST | `/api/predict` | Performance prediction |

### Example: predict

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "study_hours": 4,
    "attendance_pct": 85,
    "prior_score": 72,
    "quizzes_completed": 5
  }'
```

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Day 4 checklist

- [x] FastAPI project structure (`routes`, `models`, `services`, `database`)
- [x] GET `/api/health`
- [x] GET `/api/user`
- [x] POST `/api/predict`
- [x] CORS for frontend (`localhost:3000`)
- [ ] Live Supabase connection (optional — works without DB for demo)
