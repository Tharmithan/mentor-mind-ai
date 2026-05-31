"""Personalized learning roadmap generator (Week 6 · Day 5)."""

from __future__ import annotations

import re

from app.models.learning_planner import (
    LearningRoadmapRequest,
    LearningRoadmapResponse,
    MilestoneStatus,
    MonthlyPhase,
    MonthlyTopic,
)
from app.planner.roadmaps import GOAL_ALIASES, MONTHLY_ROADMAPS
from app.agents.career.paths import CAREER_PATHS


def resolve_goal(goal: str) -> str:
    lower = goal.lower().strip()
    for alias, cid in sorted(GOAL_ALIASES.items(), key=lambda x: -len(x[0])):
        if alias in lower:
            return cid
    for cid in MONTHLY_ROADMAPS:
        title = CAREER_PATHS.get(cid, {}).get("title", "").lower()
        if title and title in lower:
            return cid
    return "ai_engineer"


class RoadmapGenerator:
    @staticmethod
    def generate(req: LearningRoadmapRequest) -> LearningRoadmapResponse:
        career_id = resolve_goal(req.goal)
        template = MONTHLY_ROADMAPS.get(career_id, MONTHLY_ROADMAPS["ai_engineer"])
        meta = CAREER_PATHS.get(career_id, {"title": "AI Engineer"})

        months_limit = req.total_months or len(template)
        selected = template[:months_limit]

        months: list[MonthlyPhase] = []
        milestones: list[MilestoneStatus] = []

        for block in selected:
            topics = [MonthlyTopic(**t) for t in block["topics"]]
            months.append(
                MonthlyPhase(
                    month=block["month"],
                    title=block["title"],
                    topics=topics,
                    goals=block["goals"],
                    hours_per_week=req.hours_per_week,
                    milestone=block["milestone"],
                )
            )
            milestones.append(
                MilestoneStatus(
                    id=f"m{block['month']}",
                    label=block["milestone"],
                    month=block["month"],
                    completed=False,
                )
            )

        topic_preview = ", ".join(
            t.name for t in months[0].topics[:2]
        ) if months else ""
        summary = (
            f"**{len(months)}-month personalized roadmap** to {req.goal.strip()}. "
            f"Start with {topic_preview} in Month 1 at ~{req.hours_per_week}h/week."
        )

        return LearningRoadmapResponse(
            goal=req.goal.strip(),
            career_id=career_id,
            career_title=meta["title"],
            total_months=len(months),
            hours_per_week=req.hours_per_week,
            summary=summary,
            months=months,
            milestones=milestones,
        )

    @staticmethod
    def parse_goal_from_message(message: str) -> LearningRoadmapRequest | None:
        lower = message.lower()
        if not re.search(
            r"\b(become|learning plan|learning roadmap|learning planner|roadmap to|"
            r"path to|plan to become|goal:|my goal)\b",
            lower,
        ):
            return None
        hours = 10.0
        hm = re.search(r"(\d+)\s*h(?:ours?)?\s*(?:per\s*week|/week|weekly)?", lower)
        if hm:
            hours = float(hm.group(1))
        mm = re.search(r"(\d+)\s*months?", lower)
        total_months = int(mm.group(1)) if mm else None
        goal = message.strip()
        for prefix in ("i want to ", "my goal is to ", "my goal: ", "help me become "):
            if lower.startswith(prefix):
                goal = message[len(prefix):].strip()
                break
        return LearningRoadmapRequest(goal=goal, hours_per_week=hours, total_months=total_months)

    @staticmethod
    def to_markdown(result: LearningRoadmapResponse) -> str:
        lines = [
            f"## Learning Roadmap — {result.career_title}\n",
            result.summary,
            "",
        ]
        for m in result.months:
            topics = ", ".join(f"**{t.name}**" for t in m.topics)
            lines.append(f"### Month {m.month}: {m.title}")
            lines.append(f"**Topics:** {topics}")
            lines.append(f"**Goals:**")
            for g in m.goals:
                lines.append(f"• {g}")
            lines.append(f"_Milestone: {m.milestone}_")
            lines.append("")
        lines.append("**Milestones to track**")
        for ms in result.milestones:
            lines.append(f"• Month {ms.month}: {ms.label}")
        return "\n".join(lines)
