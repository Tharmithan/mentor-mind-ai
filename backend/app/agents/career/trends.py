"""Industry trend recommendations (Week 6 · Day 3)."""

from __future__ import annotations

from app.agents.career.paths import CAREER_PATHS, INDUSTRY_TRENDS
from app.agents.career.profile_builder import ProfileBuilder, resolve_career_id
from app.models.career import CareerAnalysisRequest, IndustryTrend, IndustryTrendsResponse


class IndustryTrendsService:
    @staticmethod
    def get_trends(target_career: str | None = None) -> IndustryTrendsResponse:
        career_id = resolve_career_id(target_career) or "ai_engineer"
        meta = CAREER_PATHS.get(career_id, CAREER_PATHS["ai_engineer"])

        # Rank trends by career relevance
        category_boost = {
            "data_scientist": {"Data": 2, "AI": 1, "Governance": 1},
            "ai_engineer": {"AI": 3, "Software": 1, "Governance": 1},
            "mlops_engineer": {"Infrastructure": 3, "AI": 1, "Governance": 2},
            "software_engineer": {"Software": 3, "AI": 1, "Data": 1},
        }.get(career_id, {})

        scored = []
        for t in INDUSTRY_TRENDS:
            boost = category_boost.get(t["category"], 0)
            scored.append((boost, t))
        scored.sort(key=lambda x: -x[0])

        trends = [IndustryTrend(**t) for _, t in scored]
        hot_roles = [CAREER_PATHS[c]["title"] for c in ("ai_engineer", "mlops_engineer", "data_scientist")]

        summary = (
            f"**Industry outlook for aspiring {meta['title']}s** — "
            f"AI adoption, production ML, and responsible AI are shaping hiring in 2025–2026."
        )

        return IndustryTrendsResponse(trends=trends, summary=summary, hot_roles=hot_roles)

    @staticmethod
    def from_request(req: CareerAnalysisRequest, message: str | None = None) -> IndustryTrendsResponse:
        target = req.target_career or message
        return IndustryTrendsService.get_trends(target)

    @staticmethod
    def to_markdown(result: IndustryTrendsResponse) -> str:
        lines = [result.summary, "", "**Trending now**"]
        for t in result.trends[:4]:
            lines.append(f"\n**{t.title}** ({t.category})")
            lines.append(f"_{t.relevance}_")
            lines.append(f"→ **Action:** {t.action}")
        lines.append(f"\n**Hot roles:** {', '.join(result.hot_roles)}")
        return "\n".join(lines)
