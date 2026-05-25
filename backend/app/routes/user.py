from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_optional_db
from app.models import UserResponse
from app.services import UserService

router = APIRouter()


@router.get("/user", response_model=UserResponse)
async def get_user(db: AsyncSession | None = Depends(get_optional_db)):
    """Return user profile from database (or mock if DB unavailable)."""
    user = await UserService.get_demo_user(db)
    return UserResponse(user=user)
