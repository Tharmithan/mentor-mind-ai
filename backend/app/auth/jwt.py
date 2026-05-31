"""JWT access + refresh tokens (Week 8 · Day 2)."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.config import settings

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: str, email: str, role: str) -> tuple[str, int]:
    expires_min = settings.access_token_expire_minutes
    expire = _now() + timedelta(minutes=expires_min)
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": TOKEN_TYPE_ACCESS,
        "exp": expire,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires_min * 60


def create_refresh_token(user_id: str, jti: str | None = None) -> tuple[str, str, datetime]:
    jti = jti or uuid.uuid4().hex
    days = settings.refresh_token_expire_days
    expire = _now() + timedelta(days=days)
    payload = {
        "sub": user_id,
        "jti": jti,
        "type": TOKEN_TYPE_REFRESH,
        "exp": expire,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, jti, expire


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])


def safe_decode(token: str) -> dict[str, Any] | None:
    try:
        return decode_token(token)
    except JWTError:
        return None
