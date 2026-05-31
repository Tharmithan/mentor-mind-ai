"""Weekly plan breakdown from monthly roadmap (Week 6 · Day 5)."""

from __future__ import annotations

from app.models.learning_planner import LearningRoadmapResponse, WeeklyPlanResponse, WeeklyTask


class WeeklyPlanner:
    @staticmethod
    def for_month(
        roadmap: LearningRoadmapResponse,
        month: int,
        week: int = 1,
        progress_pct: float = 0,
    ) -> WeeklyPlanResponse:
        phase = next((m for m in roadmap.months if m.month == month), roadmap.months[0])
        topic_names = [t.name for t in phase.topics]

        # Split month goals across 4 weeks
        goals = phase.goals or [f"Study {', '.join(topic_names)}"]
        weeks: list[WeeklyTask] = []
        hours_week = phase.hours_per_week

        for w in range(1, 5):
            topic_idx = (w - 1) % max(len(phase.topics), 1)
            topic = phase.topics[topic_idx] if phase.topics else None
            focus = topic.name if topic else phase.title
            tasks = WeeklyPlanner._week_tasks(topic, w, goals)
            weeks.append(
                WeeklyTask(
                    week=w,
                    focus=focus,
                    tasks=tasks,
                    hours=round(hours_week / 4 * (1.1 if w == week else 1.0), 1),
                )
            )

        current = weeks[min(week, 4) - 1]
        summary = (
            f"**Month {month} · Week {week}** — focus on **{current.focus}**. "
            f"~{current.hours}h this week toward: _{phase.milestone}_"
        )

        return WeeklyPlanResponse(
            plan_id="",
            month=month,
            month_title=phase.title,
            week=week,
            progress_pct=progress_pct,
            weeks=weeks,
            summary=summary,
        )

    @staticmethod
    def _week_tasks(topic, week: int, goals: list[str]) -> list[str]:
        if topic is None:
            return [f"Work on: {g}" for g in goals[:2]]
        base = [
            f"Study {topic.name}: {topic.description[:60]}",
            f"Resource: {topic.resources[0]}" if topic.resources else f"Practice {topic.name}",
        ]
        if week == 1:
            base.append("Set up environment and skim overview materials")
        elif week == 2:
            base.append("Hands-on exercises and mini-project")
        elif week == 3:
            base.append("Review weak areas + practice problems")
        else:
            goal = goals[(week - 1) % len(goals)] if goals else "Review and consolidate"
            base.append(f"Week goal: {goal}")
        return base[:4]

    @staticmethod
    def to_markdown(plan: WeeklyPlanResponse) -> str:
        lines = [plan.summary, ""]
        for w in plan.weeks:
            marker = " ← **this week**" if w.week == plan.week else ""
            lines.append(f"**Week {w.week} — {w.focus}** (~{w.hours}h){marker}")
            for t in w.tasks:
                lines.append(f"  • {t}")
            lines.append("")
        return "\n".join(lines)
