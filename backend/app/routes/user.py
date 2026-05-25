from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import UserResponse
from app.services import UserService

router = APIRouter()


@router.get("/user", response_model=UserResponse)
async def get_user(db: AsyncSession = Depends(get_db)):
    """Return user profile from database (or mock if empty)."""
    user = await UserService.get_demo_user(db)
    return UserResponse(user=user)
