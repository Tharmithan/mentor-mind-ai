"""Admin routes — monitor users and models (Week 8 · Bonus).

    GET /api/admin/overview   platform stats for admin dashboard
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth.dependencies import get_current_user_required
from app.database import get_optional_db
from app.models.admin import AdminOverviewResponse
from app.models.auth import AuthUserProfile
from app.services.admin_service import AdminService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/admin", tags=["admin"])


def _require_admin(user: AuthUserProfile = Depends(get_current_user_required)) -> AuthUserProfile:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


@router.get("/overview", response_model=AdminOverviewResponse)
async def admin_overview(
    _admin: AuthUserProfile = Depends(_require_admin),
    db: AsyncSession | None = Depends(get_optional_db),
) -> AdminOverviewResponse:
    return await AdminService.overview(db)


@router.get("/overview/demo", response_model=AdminOverviewResponse)
async def admin_overview_demo(
    db: AsyncSession | None = Depends(get_optional_db),
) -> AdminOverviewResponse:
    """Demo admin stats without auth (local dev / portfolio)."""
    return await AdminService.overview(db)
