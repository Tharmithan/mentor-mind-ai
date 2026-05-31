"""Learning roadmap generation per career path (Week 6 · Day 3)."""

from __future__ import annotations

from app.agents.career.paths import CAREER_PATHS, ROADMAP_TEMPLATES
from app.agents.career.profile_builder import ProfileBuilder, resolve_career_id
from app.agents.career.skill_gap import SkillGapAnalyzer
from app.models.career import CareerAnalysisRequest, LearningRoadmapResponse, RoadmapPhase


class RoadmapGenerator:
    @staticmethod
    def generate(career_id: str, profile=None) -> LearningRoadmapResponse:
        meta = CAREER_PATHS.get(career_id, CAREER_PATHS["data_scientist"])
        template = ROADMAP_TEMPLATES.get(career_id, ROADMAP_TEMPLATES["data_scientist"])

        phases: list[RoadmapPhase] = []
        for block in template:
            phases.append(RoadmapPhase(**block))

        total_weeks = sum(p.duration_weeks for p in phases)
        milestones = [
            f"Week {sum(p.duration_weeks for p in phases[:i+1])}: Complete {p.phase} phase"
            for i, p in enumerate(phases)
        ]

        gap_note = ""
        if profile is not None:
            gap_result = SkillGapAnalyzer.analyze(profile, career_id)
            high_gaps = [g.skill for g in gap_result.gaps if g.priority == "high"][:2]
            if high_gaps:
                gap_note = f" Prioritize closing gaps in: {', '.join(high_gaps)}."

        summary = (
            f"**{total_weeks}-week roadmap** to become a {meta['title']}. "
            f"{meta['tagline']}.{gap_note}"
        )

        return LearningRoadmapResponse(
            career=meta["title"],
            total_weeks=total_weeks,
            phases=phases,
            summary=summary,
            milestones=milestones,
        )

    @staticmethod
    def from_request(req: CareerAnalysisRequest, message: str | None = None) -> LearningRoadmapResponse:
        profile = ProfileBuilder.build(
            message=message,
            interests=req.interests,
            subject_scores=req.subject_scores,
            interview_session_id=req.interview_session_id,
        )
        career_id = resolve_career_id(req.target_career or message) or "data_scientist"
        return RoadmapGenerator.generate(career_id, profile)

    @staticmethod
    def to_markdown(result: LearningRoadmapResponse) -> str:
        lines = [result.summary, ""]
        for phase in result.phases:
            lines.append(f"### {phase.phase} ({phase.duration_weeks} weeks)")
            lines.append("**Goals**")
            for g in phase.goals:
                lines.append(f"• {g}")
            lines.append("**Skills:** " + ", ".join(s.replace("_", " ") for s in phase.skills))
            lines.append("**Resources:** " + ", ".join(phase.resources[:3]))
            lines.append("")
        lines.append("**Milestones**")
        for m in result.milestones:
            lines.append(f"• {m}")
        return "\n".join(lines)
