"""Career Agent service orchestration (Week 6 · Day 3)."""

from __future__ import annotations

from app.agents.career.profile_builder import ProfileBuilder
from app.agents.career.recommendation_engine import CareerRecommendationEngine
from app.agents.career.roadmap_generator import RoadmapGenerator
from app.agents.career.skill_gap import SkillGapAnalyzer
from app.agents.career.trends import IndustryTrendsService
from app.models.career import CareerAnalysisRequest

__all__ = ["CareerAgentService"]


class CareerAgentService:
    recommend = staticmethod(CareerRecommendationEngine.from_request)
    skill_gaps = staticmethod(SkillGapAnalyzer.from_request)
    roadmap = staticmethod(RoadmapGenerator.from_request)
    trends = staticmethod(IndustryTrendsService.from_request)
    build_profile = staticmethod(ProfileBuilder.build)

    @staticmethod
    async def full_analysis(req: CareerAnalysisRequest, message: str | None = None) -> dict:
        rec = await CareerRecommendationEngine.from_request(req, message)
        career_id = rec.top_career.career_id
        profile = ProfileBuilder.build(
            message=message,
            interests=req.interests,
            subject_scores=req.subject_scores,
            interview_session_id=req.interview_session_id,
        )
        gaps = SkillGapAnalyzer.analyze(profile, career_id)
        roadmap = RoadmapGenerator.generate(career_id, profile)
        trends = IndustryTrendsService.get_trends(career_id)
        return {
            "recommendation": rec,
            "skill_gaps": gaps,
            "roadmap": roadmap,
            "trends": trends,
        }
