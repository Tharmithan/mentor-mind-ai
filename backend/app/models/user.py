from pydantic import BaseModel, EmailStr, Field


class UserProfile(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: str = "student"
    xp: int = 0
    streak_days: int = 0
    performance_score: float = Field(ge=0, le=100)


class UserResponse(BaseModel):
    user: UserProfile
