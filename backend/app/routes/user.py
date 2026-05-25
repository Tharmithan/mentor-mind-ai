from fastapi import APIRouter

from app.models import UserResponse
from app.services import UserService

router = APIRouter()


@router.get("/user", response_model=UserResponse)
async def get_user():
    """Return current user profile (demo until JWT auth in Phase 2)."""
    user = await UserService.get_demo_user()
    return UserResponse(user=user)
