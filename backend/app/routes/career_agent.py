"""Career Agent routes (Week 6 · Day 3).

    POST /api/agents/career/recommend       career path recommendation
    POST /api/agents/career/skill-gaps        skill gap analysis
    POST /api/agents/career/roadmap           learning roadmap
    GET  /api/agents/career/trends            industry trends
    POST /api/agents/career/analyze           full analysis bundle
"""

from fastapi import APIRouter

from app.agents.career.service import CareerAgentService
from app.agents.career.trends import IndustryTrendsService
from app.models.career import (
    CareerAnalysisRequest,
    CareerRecommendationResponse,
    IndustryTrendsResponse,
    LearningRoadmapResponse,
    SkillGapAnalysisResponse,
)

router = APIRouter(prefix="/agents/career", tags=["career-agent"])


@router.post("/recommend", response_model=CareerRecommendationResponse)
async def recommend_career(body: CareerAnalysisRequest) -> CareerRecommendationResponse:
    return await CareerAgentService.recommend(body)


@router.post("/skill-gaps", response_model=SkillGapAnalysisResponse)
async def skill_gaps(body: CareerAnalysisRequest) -> SkillGapAnalysisResponse:
    return CareerAgentService.skill_gaps(body)


@router.post("/roadmap", response_model=LearningRoadmapResponse)
async def learning_roadmap(body: CareerAnalysisRequest) -> LearningRoadmapResponse:
    return CareerAgentService.roadmap(body)


@router.get("/trends", response_model=IndustryTrendsResponse)
async def industry_trends(target_career: str | None = None) -> IndustryTrendsResponse:
    return IndustryTrendsService.from_request(CareerAnalysisRequest(target_career=target_career))


@router.post("/analyze")
async def full_career_analysis(body: CareerAnalysisRequest) -> dict:
    bundle = await CareerAgentService.full_analysis(body)
    return {
        "recommendation": bundle["recommendation"].model_dump(),
        "skill_gaps": bundle["skill_gaps"].model_dump(),
        "roadmap": bundle["roadmap"].model_dump(),
        "trends": bundle["trends"].model_dump(),
    }
