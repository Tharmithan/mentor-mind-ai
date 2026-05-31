"""Authentication routes (Week 8 · Day 2).

    POST /api/auth/register   create account + tokens
    POST /api/auth/login      login + tokens
    POST /api/auth/refresh    rotate refresh token
    POST /api/auth/logout     revoke refresh token
    GET  /api/auth/me         current user from access token
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Request

from app.auth.dependencies import get_current_user_required
from app.auth.rate_limit import limiter
from app.auth.service import AuthService
from app.config import settings
from app.database import get_optional_db
from app.models.auth import (
    AuthUserProfile,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])


@limiter.limit(f"{settings.auth_rate_limit_per_minute}/minute")
@router.post("/register", response_model=TokenResponse)
async def register(
    request: Request,
    payload: Annotated[RegisterRequest, Body()],
    db: AsyncSession | None = Depends(get_optional_db),
) -> TokenResponse:
    return await AuthService.register(db, payload)


@limiter.limit(f"{settings.auth_rate_limit_per_minute}/minute")
@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    payload: Annotated[LoginRequest, Body()],
    db: AsyncSession | None = Depends(get_optional_db),
) -> TokenResponse:
    return await AuthService.login(db, payload)


@limiter.limit(f"{settings.auth_rate_limit_per_minute}/minute")
@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    request: Request,
    payload: Annotated[RefreshRequest, Body()],
    db: AsyncSession | None = Depends(get_optional_db),
) -> TokenResponse:
    return await AuthService.refresh(db, payload.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    payload: Annotated[RefreshRequest, Body()],
    db: AsyncSession | None = Depends(get_optional_db),
) -> MessageResponse:
    await AuthService.logout(db, payload.refresh_token)
    return MessageResponse(message="Logged out")


@router.get("/me", response_model=AuthUserProfile)
async def me(user: AuthUserProfile = Depends(get_current_user_required)) -> AuthUserProfile:
    return user
