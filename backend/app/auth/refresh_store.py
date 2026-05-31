"""Refresh token persistence — DB + JSON fallback (Week 8 · Day 2)."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.refresh_token import RefreshToken

AUTH_DIR = Path(__file__).resolve().parents[2] / "uploads" / "auth"
TOKENS_JSON = AUTH_DIR / "refresh_tokens.json"


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


class RefreshTokenStore:
    @staticmethod
    async def save(
        session: AsyncSession | None,
        user_id: str,
        raw_token: str,
        jti: str,
        expires_at: datetime,
    ) -> None:
        token_hash = _hash_token(raw_token)
        if session is not None:
            try:
                uid = uuid.UUID(user_id)
            except ValueError:
                uid = uuid.uuid4()
            row = RefreshToken(
                user_id=uid,
                token_hash=token_hash,
                jti=jti,
                expires_at=expires_at,
                revoked=False,
            )
            session.add(row)
            await session.commit()
            return

        AUTH_DIR.mkdir(parents=True, exist_ok=True)
        entries = RefreshTokenStore._load_file()
        entries.append(
            {
                "jti": jti,
                "user_id": user_id,
                "token_hash": token_hash,
                "expires_at": expires_at.isoformat(),
                "revoked": False,
            }
        )
        RefreshTokenStore._save_file(entries[-500:])

    @staticmethod
    async def is_valid(
        session: AsyncSession | None,
        raw_token: str,
        jti: str,
        user_id: str,
    ) -> bool:
        token_hash = _hash_token(raw_token)
        if session is not None:
            try:
                uid = uuid.UUID(user_id)
            except ValueError:
                return False
            result = await session.execute(
                select(RefreshToken).where(
                    RefreshToken.jti == jti,
                    RefreshToken.user_id == uid,
                    RefreshToken.revoked.is_(False),
                )
            )
            row = result.scalar_one_or_none()
            if row is None or row.token_hash != token_hash:
                return False
            if row.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
                return False
            return True

        for e in RefreshTokenStore._load_file():
            if e.get("jti") != jti or e.get("user_id") != user_id:
                continue
            if e.get("revoked") or e.get("token_hash") != token_hash:
                return False
            exp = datetime.fromisoformat(e["expires_at"])
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)
            return exp >= datetime.now(timezone.utc)
        return False

    @staticmethod
    async def revoke(session: AsyncSession | None, jti: str) -> None:
        if session is not None:
            result = await session.execute(select(RefreshToken).where(RefreshToken.jti == jti))
            row = result.scalar_one_or_none()
            if row:
                row.revoked = True
                await session.commit()
            return

        entries = RefreshTokenStore._load_file()
        for e in entries:
            if e.get("jti") == jti:
                e["revoked"] = True
        RefreshTokenStore._save_file(entries)

    @staticmethod
    def _load_file() -> list[dict]:
        if not TOKENS_JSON.exists():
            return []
        return json.loads(TOKENS_JSON.read_text(encoding="utf-8"))

    @staticmethod
    def _save_file(entries: list[dict]) -> None:
        AUTH_DIR.mkdir(parents=True, exist_ok=True)
        TOKENS_JSON.write_text(json.dumps(entries, indent=2), encoding="utf-8")


def _is_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False
