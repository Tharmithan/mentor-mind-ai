from pydantic import BaseModel


class RecommendationItem(BaseModel):
    id: str
    title: str
    description: str | None
    topic: str | None
    priority: str
    is_completed: bool
    action_type: str | None = None


class RecommendationsResponse(BaseModel):
    recommendations: list[RecommendationItem]
