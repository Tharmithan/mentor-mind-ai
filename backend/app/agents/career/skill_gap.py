"""Skill gap analysis vs target career (Week 6 · Day 3)."""

from __future__ import annotations

from app.agents.career.paths import CAREER_PATHS, SKILL_RESOURCES
from app.agents.career.profile_builder import ProfileBuilder, resolve_career_id
from app.models.career import CareerAnalysisRequest, SkillGapAnalysisResponse, SkillGapItem, StudentCareerProfile


class SkillGapAnalyzer:
    @staticmethod
    def analyze(profile: StudentCareerProfile, career_id: str) -> SkillGapAnalysisResponse:
        meta = CAREER_PATHS.get(career_id)
        if not meta:
            career_id = "data_scientist"
            meta = CAREER_PATHS[career_id]

        gaps: list[SkillGapItem] = []
        readiness_parts: list[float] = []

        for skill, required in meta["required_skills"].items():
            current = profile.skills.get(skill, 50)
            gap = max(0, required - current)
            ratio = min(1.0, current / required) if required else 1.0
            readiness_parts.append(ratio)
            if gap <= 5:
                continue
            priority = "high" if gap >= 25 else "medium" if gap >= 12 else "low"
            resources = SKILL_RESOURCES.get(skill, ["Online course + hands-on project"])
            gaps.append(
                SkillGapItem(
                    skill=skill.replace("_", " ").title(),
                    current_level=round(current, 1),
                    required_level=float(required),
                    gap=round(gap, 1),
                    priority=priority,
                    learning_actions=[
                        f"Target {required}% proficiency (currently {current:.0f}%)",
                        f"Study: {resources[0]}",
                        "Apply skill in a mini project within 2 weeks",
                    ],
                )
            )

        gaps.sort(key=lambda g: -g.gap)
        overall = (sum(readiness_parts) / len(readiness_parts) * 100) if readiness_parts else 0

        summary = (
            f"You are **{overall:.0f}% ready** for **{meta['title']}**. "
            f"{len([g for g in gaps if g.priority == 'high'])} high-priority gaps to close."
        )

        return SkillGapAnalysisResponse(
            target_career=meta["title"],
            overall_readiness=round(overall, 1),
            gaps=gaps[:8],
            summary=summary,
        )

    @staticmethod
    def from_request(req: CareerAnalysisRequest, message: str | None = None) -> SkillGapAnalysisResponse:
        profile = ProfileBuilder.build(
            message=message,
            interests=req.interests,
            subject_scores=req.subject_scores,
            interview_session_id=req.interview_session_id,
        )
        career_id = resolve_career_id(req.target_career or message) or "data_scientist"
        return SkillGapAnalyzer.analyze(profile, career_id)

    @staticmethod
    def to_markdown(result: SkillGapAnalysisResponse) -> str:
        lines = [f"**Skill gap analysis — {result.target_career}**\n", result.summary, ""]
        if not result.gaps:
            lines.append("You're well-aligned with this role — focus on portfolio projects and interviews.")
            return "\n".join(lines)
        for g in result.gaps:
            lines.append(
                f"**{g.skill}** [{g.priority}] — {g.current_level:.0f}% → {g.required_level:.0f}% "
                f"(gap: {g.gap:.0f})"
            )
            for action in g.learning_actions[:2]:
                lines.append(f"  - {action}")
            lines.append("")
        return "\n".join(lines)
