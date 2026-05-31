"""Career Agent — career recommendations, skill gaps, roadmaps, trends (Week 6 · Day 3)."""

from __future__ import annotations

import re

from app.agents.career.profile_builder import resolve_career_id
from app.agents.career.recommendation_engine import CareerRecommendationEngine
from app.agents.career.roadmap_generator import RoadmapGenerator
from app.agents.career.skill_gap import SkillGapAnalyzer
from app.agents.career.trends import IndustryTrendsService
from app.ai.insights_service import InsightsService
from app.models.career import CareerAnalysisRequest
from app.models.insights import InsightsRequest
from app.rag.llm import call_llm, llm_enabled


async def run_career_agent(message: str, context: dict) -> dict:
    lower = message.lower()
    req = CareerAnalysisRequest(
        interests=context.get("interests"),
        target_career=context.get("target_career"),
        subject_scores=context.get("subject_scores"),
        interview_session_id=context.get("interview_session_id"),
    )

    # --- Week 6 Day 3: career path intelligence ---

    if re.search(
        r"\b(roadmap|learning path|career plan|how to become|get started as|"
        r"transition to|path to|learning roadmap)\b",
        lower,
    ):
        roadmap = RoadmapGenerator.from_request(req, message)
        return {
            "answer": RoadmapGenerator.to_markdown(roadmap),
            "used_llm": False,
            "sub_intent": "learning_roadmap",
            "data": roadmap.model_dump(),
            "actions": [{"type": "navigate", "path": "/dashboard"}],
        }

    if re.search(
        r"\b(career path|career recommend|which career|best career|what career|"
        r"should i become|help me choose|career fit)\b",
        lower,
    ) or (
        re.search(r"\b(data scientist|ai engineer|mlops|software engineer)\b", lower)
        and not re.search(r"\b(roadmap|skill gap|trend)\b", lower)
    ):
        result = await CareerRecommendationEngine.from_request(req, message)
        return {
            "answer": CareerRecommendationEngine.to_markdown(result),
            "used_llm": result.used_llm,
            "sub_intent": "career_recommendation",
            "data": {
                "top_career": result.top_career.model_dump(),
                "alternatives": [a.model_dump() for a in result.alternatives],
            },
            "actions": [{"type": "navigate", "path": "/dashboard"}],
        }

    if re.search(r"\b(skill gap|skills gap|gap analysis|what skills|missing skills|upskill)\b", lower):
        target = resolve_career_id(context.get("target_career") or message)
        req.target_career = target
        gaps = SkillGapAnalyzer.from_request(req, message)
        return {
            "answer": SkillGapAnalyzer.to_markdown(gaps),
            "used_llm": False,
            "sub_intent": "skill_gap",
            "data": gaps.model_dump(),
            "actions": [{"type": "navigate", "path": "/dashboard"}],
        }

    if re.search(
        r"\b(industry trend|job market|hiring trend|in demand|hot roles|future of|"
        r"market outlook)\b",
        lower,
    ):
        trends = IndustryTrendsService.from_request(req, message)
        return {
            "answer": IndustryTrendsService.to_markdown(trends),
            "used_llm": False,
            "sub_intent": "industry_trends",
            "data": trends.model_dump(),
            "actions": [{"type": "navigate", "path": "/dashboard"}],
        }

    # --- Week 6 Day 1: performance insights ---

    if any(w in lower for w in ("insight", "performance", "weak", "improve", "grade", "predict")):
        try:
            insights = InsightsService.generate(InsightsRequest())
            top = insights.insights[:3]
            lines = [f"• **{i.title}** — {i.message}" for i in top]
            answer = "**Career & performance insights**\n\n" + "\n".join(lines)
            summary = insights.performance_summary
            answer += f"\n\n_Overall trend: {summary.overall_trend}_"
            answer += (
                "\n\nAsk me: _\"Which career path fits me best?\"_ for AI Engineer, "
                "Data Scientist, MLOps, or Software Engineer recommendations."
            )
            return {
                "answer": answer,
                "used_llm": False,
                "sub_intent": "insights",
                "actions": [{"type": "navigate", "path": "/dashboard"}],
            }
        except Exception:
            pass

    # Default: run full career recommendation
    result = await CareerRecommendationEngine.from_request(req, message)
    if result.top_career.match_score >= 50:
        return {
            "answer": CareerRecommendationEngine.to_markdown(result),
            "used_llm": result.used_llm,
            "sub_intent": "career_recommendation",
            "data": {"top_career": result.top_career.model_dump()},
            "actions": [{"type": "navigate", "path": "/dashboard"}],
        }

    if llm_enabled():
        raw = await call_llm(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a career counselor for students interested in "
                        "AI Engineer, Data Scientist, MLOps Engineer, or Software Engineer roles. "
                        "Give practical, encouraging advice."
                    ),
                },
                {"role": "user", "content": message},
            ],
            max_tokens=500,
        )
        if raw:
            return {
                "answer": raw,
                "used_llm": True,
                "sub_intent": "career_advice",
                "actions": [{"type": "navigate", "path": "/dashboard"}],
            }

    return {
        "answer": (
            "I'm your **Career Agent**. I analyze your skills, interests, performance, "
            "and interview scores to recommend career paths.\n\n"
            "**Try asking:**\n"
            "• _\"Which career path fits me best?\"_\n"
            "• _\"Skill gap analysis for Data Scientist\"_\n"
            "• _\"Learning roadmap to become an AI Engineer\"_\n"
            "• _\"What are the industry trends for ML roles?\"_"
        ),
        "used_llm": False,
        "sub_intent": "help",
        "actions": [{"type": "navigate", "path": "/dashboard"}],
    }
