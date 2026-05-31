# Week 8 · Day 3 — Testing

Ensure everything works with unit, integration, and end-to-end tests.

---

## Test coverage

| Area | Tests | File |
|------|-------|------|
| **User — signup** | Register + validation | `tests/integration/test_auth_api.py` |
| **User — login** | Login + invalid password | `tests/integration/test_auth_api.py` |
| **User — logout** | Refresh rotation + logout | `tests/integration/test_auth_api.py` |
| **AI — prediction** | POST /api/predict | `tests/integration/test_ai_api.py` |
| **AI — recommendations** | GET /api/recommendations | `tests/integration/test_ai_api.py` |
| **RAG chatbot** | Upload → search → chat | `tests/integration/test_rag_api.py` |
| **Interview coach** | Start → answer → session | `tests/integration/test_interview_api.py` |
| **Database CRUD** | User + performance + recs | `tests/integration/test_database_crud.py` |
| **E2E flows** | Auth → MLOps, predict → monitor | `tests/e2e/test_flows.py` |
| **Unit** | bcrypt, JWT | `tests/unit/` |

---

## Run locally

```bash
cd backend
pip install -r requirements.txt -r requirements-test.txt
pytest -v
```

Or from repo root:

```bash
chmod +x scripts/run-tests.sh
./scripts/run-tests.sh
```

---

## Structure

```
backend/tests/
  conftest.py              # SQLite in-memory DB + TestClient
  unit/
    test_passwords.py
    test_jwt.py
  integration/
    test_auth_api.py
    test_ai_api.py
    test_rag_api.py
    test_interview_api.py
    test_database_crud.py
  e2e/
    test_flows.py
```

---

## CI

GitHub Actions runs on every push/PR to `main`:

`.github/workflows/tests.yml`

---

## Fixtures

- **`client`** — FastAPI TestClient with in-memory SQLite
- **`unique_email`** — avoids register collisions
- **`auth_headers`** — pre-registered user Bearer token
- Rate limiting disabled in tests

---

## Example output

```bash
pytest -v
# tests/unit/test_passwords.py::test_hash_and_verify_password PASSED
# tests/integration/test_auth_api.py::test_register_login_me_logout PASSED
# tests/integration/test_ai_api.py::test_predict_performance PASSED
# tests/e2e/test_flows.py::test_e2e_auth_to_protected_mlops PASSED
```

---

## Next (Week 8)

| Day | Focus |
|-----|-------|
| 4 | Professional GitHub |
| 5 | Portfolio website |
| 6 | Demo video |
| 7 | Resume-ready summary |
