"""Auth dependencies for protected routes (Week 8 · Day 2)."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.service import AuthService
from app.models.auth import AuthUserProfile

_bearer = HTTPBearer(auto_error=False)


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> AuthUserProfile | None:
    if credentials is None:
        return None
    return AuthService.user_from_access_token(credentials.credentials)


async def get_current_user_required(
    user: AuthUserProfile | None = Depends(get_current_user_optional),
) -> AuthUserProfile:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_admin(
    user: AuthUserProfile = Depends(get_current_user_required),
) -> AuthUserProfile:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
