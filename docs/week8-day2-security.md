# Week 8 · Day 2 — Security

Protect the application with JWT authentication, refresh tokens, password hashing, rate limiting, and safe error handling.

---

## What was added

| Feature | Implementation |
|---------|----------------|
| **JWT access tokens** | Short-lived (30 min), Bearer auth |
| **Refresh tokens** | 7-day rotation, stored hashed in DB or JSON fallback |
| **Password hashing** | bcrypt via passlib |
| **Input validation** | Pydantic validators on register/login |
| **Rate limiting** | slowapi — 10/min auth, global middleware |
| **Security headers** | X-Frame-Options, nosniff, Referrer-Policy |
| **Error handling** | No secret leakage when `DEBUG=false` |
| **Protected routes** | MLOps promote + experiment run require auth |

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/register` | No | Create account |
| POST | `/api/auth/login` | No | Login |
| POST | `/api/auth/refresh` | Refresh token | Rotate tokens |
| POST | `/api/auth/logout` | Refresh token | Revoke refresh token |
| GET | `/api/auth/me` | Bearer | Current user |

---

## Demo credentials

After seeding (`python -m scripts.seed_db`):

```
Email:    student@mentormind.ai
Password: Demo123!
```

Without database (offline demo):

```
POST /api/auth/login
{"email":"student@mentormind.ai","password":"Demo123!"}
```

---

## Usage

### Register

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "new@example.com",
    "password": "SecurePass1",
    "full_name": "New Student"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@mentormind.ai","password":"Demo123!"}'
```

Response:

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": { "id": "...", "email": "...", "role": "student" }
}
```

### Authenticated request

```bash
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Refresh

```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"YOUR_REFRESH_TOKEN"}'
```

### Protected MLOps (requires login)

```bash
curl -X POST http://localhost:8000/api/mlops/models/promote \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"version":"v3"}'
```

---

## Security checklist

- [x] Passwords hashed with bcrypt (never stored plain)
- [x] JWT signed with `JWT_SECRET` (set strong secret in production)
- [x] Refresh tokens stored as SHA-256 hash only
- [x] Token rotation on refresh (old token revoked)
- [x] Rate limit on auth endpoints (brute-force protection)
- [x] Security headers on all responses
- [x] Validation errors return field-level messages (no stack traces)
- [x] 500 errors hide details when `DEBUG=false`
- [x] API keys only in `.env` — never in code or error responses

---

## Production env

```env
JWT_SECRET=<openssl rand -hex 32>
DEBUG=false
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
AUTH_RATE_LIMIT_PER_MINUTE=10
```

Run updated schema on Supabase:

```sql
-- docs/database/schema.sql (refresh_tokens table)
```

---

## Architecture

```
Client → Bearer access token → FastAPI dependency → Route handler
                ↓ expired
         POST /auth/refresh → new access + refresh (rotation)
```

---

## File layout

```
backend/app/auth/
  passwords.py      bcrypt hash/verify
  jwt.py            access + refresh JWT
  refresh_store.py  hashed token persistence
  service.py        register, login, refresh
  dependencies.py   get_current_user_*
  rate_limit.py     slowapi limiter

backend/app/middleware/security_headers.py
backend/app/core/exceptions.py
backend/app/routes/auth.py
```

---

## Next (Week 8)

| Day | Focus |
|-----|-------|
| 3 | Testing (pytest, API smoke tests) |
| 4 | Professional GitHub |
| 5 | Portfolio website |
| 6 | Demo video |
| 7 | Resume-ready summary |
