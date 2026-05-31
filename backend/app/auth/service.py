"""Authentication service — register, login, refresh (Week 8 · Day 2)."""

from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    safe_decode,
)
from app.auth.passwords import hash_password, verify_password
from app.auth.refresh_store import RefreshTokenStore
from app.database.models import User
from app.models.auth import AuthUserProfile, LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    @staticmethod
    async def register(session: AsyncSession | None, body: RegisterRequest) -> TokenResponse:
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Registration requires a database connection",
            )

        existing = await session.scalar(select(User).where(User.email == body.email))
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        user = User(
            email=body.email,
            password_hash=hash_password(body.password),
            full_name=body.full_name,
            role="student",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return await AuthService._issue_tokens(session, user)

    @staticmethod
    async def login(session: AsyncSession | None, body: LoginRequest) -> TokenResponse:
        if session is None:
            if body.email == "student@mentormind.ai" and body.password == "Demo123!":
                return AuthService._demo_tokens()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database unavailable — use demo credentials or connect Postgres",
            )

        user = await session.scalar(select(User).where(User.email == body.email))
        if user is None or not verify_password(body.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        return await AuthService._issue_tokens(session, user)

    @staticmethod
    async def refresh(session: AsyncSession | None, raw_refresh: str) -> TokenResponse:
        payload = safe_decode(raw_refresh)
        if not payload or payload.get("type") != TOKEN_TYPE_REFRESH:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user_id = payload.get("sub")
        jti = payload.get("jti")
        if not user_id or not jti:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        valid = await RefreshTokenStore.is_valid(session, raw_refresh, jti, user_id)
        if not valid:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired or revoked")

        await RefreshTokenStore.revoke(session, jti)

        if session is None:
            return AuthService._demo_tokens()

        try:
            uid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

        user = await session.scalar(select(User).where(User.id == uid))
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

        return await AuthService._issue_tokens(session, user)

    @staticmethod
    async def logout(session: AsyncSession | None, raw_refresh: str) -> None:
        payload = safe_decode(raw_refresh)
        if payload and payload.get("jti"):
            await RefreshTokenStore.revoke(session, payload["jti"])

    @staticmethod
    async def _issue_tokens(session: AsyncSession | None, user: User) -> TokenResponse:
        user_id = str(user.id)
        access, expires_in = create_access_token(user_id, user.email, user.role)
        refresh, jti, expires_at = create_refresh_token(user_id)
        await RefreshTokenStore.save(session, user_id, refresh, jti, expires_at)
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=expires_in,
            user=AuthUserProfile(
                id=user_id,
                email=user.email,
                full_name=user.full_name or "Student",
                role=user.role,
            ),
        )

    @staticmethod
    def _demo_tokens() -> TokenResponse:
        access, expires_in = create_access_token("demo-user-001", "student@mentormind.ai", "student")
        refresh, _, _ = create_refresh_token("demo-user-001")
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            expires_in=expires_in,
            user=AuthUserProfile(
                id="demo-user-001",
                email="student@mentormind.ai",
                full_name="Demo Student",
                role="student",
            ),
        )

    @staticmethod
    def user_from_access_token(token: str) -> AuthUserProfile | None:
        payload = safe_decode(token)
        if not payload or payload.get("type") != TOKEN_TYPE_ACCESS:
            return None
        sub = payload.get("sub")
        email = payload.get("email")
        if not sub or not email:
            return None
        return AuthUserProfile(
            id=sub,
            email=email,
            full_name=payload.get("name", "Student"),
            role=payload.get("role", "student"),
        )
