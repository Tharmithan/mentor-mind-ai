"""Career Agent — insights, study plans, recommendations (Week 6 · Day 1)."""

from __future__ import annotations

from app.ai.insights_service import InsightsService
from app.models.insights import InsightsRequest
from app.rag.llm import call_llm, llm_enabled
from app.services.study_planner_service import StudyPlannerService


async def run_career_agent(message: str, context: dict) -> dict:
    lower = message.lower()

    if any(w in lower for w in ("study plan", "today", "schedule", "what should i study")):
        try:
            plan = StudyPlannerService.daily_study_planner()
            lines = [
                f"• {slot.time_slot} — **{slot.subject}**: {slot.task}"
                for slot in plan.timetable[:5]
            ]
            answer = f"**Today's study plan**\n\n{plan.summary}\n\n" + "\n".join(lines)
            return {
                "answer": answer,
                "used_llm": False,
                "sub_intent": "study_plan",
                "actions": [{"type": "navigate", "path": "/dashboard"}],
            }
        except Exception:
            pass

    if any(w in lower for w in ("insight", "performance", "weak", "improve", "grade", "predict")):
        try:
            insights = InsightsService.generate(InsightsRequest())
            top = insights.insights[:3]
            lines = [f"• **{i.title}** — {i.message}" for i in top]
            answer = "**Career & performance insights**\n\n" + "\n".join(lines)
            summary = insights.performance_summary
            answer += f"\n\n_Overall trend: {summary.overall_trend}_"
            return {
                "answer": answer,
                "used_llm": False,
                "sub_intent": "insights",
                "actions": [{"type": "navigate", "path": "/dashboard"}],
            }
        except Exception:
            pass

    if llm_enabled():
        raw = await call_llm(
            [
                {
                    "role": "system",
                    "content": (
                        "You are a career and learning copilot for students. "
                        "Give practical advice on skills, internships, and learning paths."
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
            "I'm your **Career Agent**. I can:\n"
            "• Analyze performance trends (Dashboard)\n"
            "• Suggest a daily study plan\n"
            "• Recommend focus areas\n\n"
            "Try: _\"What should I focus on this week?\"_ or open the [Dashboard](/dashboard)."
        ),
        "used_llm": False,
        "sub_intent": "help",
        "actions": [{"type": "navigate", "path": "/dashboard"}],
    }
