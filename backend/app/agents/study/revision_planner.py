"""Revision planner — phased schedule from weak subjects (Week 6 · Day 2)."""

from __future__ import annotations

import re

from app.agents.study.curricula import LEARNING_RESOURCES
from app.models.study_plan import PersonalizedRecommendationsRequest, SubjectScoreInput
from app.models.study_tutor import RevisionPhase, RevisionPlanRequest, RevisionPlanResponse
from app.recommendation.engine import StudentProfile, get_recommendation_engine
from app.services.study_planner_service import StudyPlannerService


def parse_revision_request(message: str) -> tuple[str | None, int]:
    lower = message.lower()
    days = 14
    dm = re.search(r"(\d+)\s*days?", lower)
    if dm:
        days = int(dm.group(1))
    subject = None
    for key in ("machine learning", "data structures", "programming", "mathematics"):
        if key in lower:
            subject = key.title() if key != "machine learning" else "Machine Learning"
            break
    return subject, days


class RevisionPlanner:
    @staticmethod
    def build(req: RevisionPlanRequest) -> RevisionPlanResponse:
        engine = get_recommendation_engine()
        scores = req.subject_scores or engine.default_subject_scores()
        profile = StudentProfile(subject_scores=scores)
        profile = engine.normalize_profile(profile)

        rec = StudyPlannerService.generate_recommendations(
            PersonalizedRecommendationsRequest(
                subject_scores=[SubjectScoreInput(subject=s, score=sc) for s, sc in scores.items()]
            )
        )
        weak = rec.weak_subjects
        order = rec.revision_order

        weeks = max(1, min(4, (req.days_until_exam + 6) // 7))
        phases: list[RevisionPhase] = []

        weak_names = [w.subject for w in weak] or order[:2]
        for w in range(weeks):
            if w == 0:
                focus = weak_names[:2]
                tasks = [
                    f"Deep revision: {focus[0]} weak topics (90 min/day)" if focus else "Review weakest subject",
                    "Create flashcards for key definitions",
                    "Complete 5 practice problems",
                ]
            elif w == weeks - 1:
                focus = [req.exam_subject] if req.exam_subject else order[:1]
                tasks = [
                    "Timed mock exam or mixed quiz",
                    "Review mistake log",
                    "Light revision only — no new topics",
                ]
            else:
                idx = w % max(len(order), 1)
                focus = order[idx : idx + 2] or order[:2]
                tasks = [
                    f"Rotate through {', '.join(focus)}",
                    "Summarize each topic in your own words",
                    "Pair study or teach-back session (30 min)",
                ]
            topics: list[str] = []
            for subj in focus:
                topics.append(engine._topic_for_subject(subj, scores.get(subj, 70)))
            phases.append(
                RevisionPhase(
                    week=w + 1,
                    subjects=focus,
                    focus_topics=topics,
                    daily_hours=2.0 if w < weeks - 1 else 1.5,
                    tasks=tasks,
                )
            )

        weak_analysis = [
            {
                "subject": w.subject,
                "score": w.score,
                "priority": "high" if w.score < 65 else "medium",
            }
            for w in weak
        ]

        exam = req.exam_subject or (order[0] if order else "your subjects")
        summary = (
            f"**{req.days_until_exam}-day revision plan** before your {exam} exam. "
            f"Start with weak areas ({', '.join(w.subject for w in weak[:2]) or 'priority subjects'}), "
            f"then rotate through {', '.join(order[:3])}."
        )

        return RevisionPlanResponse(
            exam_subject=req.exam_subject,
            days_until_exam=req.days_until_exam,
            weak_subjects=weak_analysis,
            revision_order=order,
            phases=phases,
            summary=summary,
        )

    @staticmethod
    def to_markdown(plan: RevisionPlanResponse) -> str:
        lines = [plan.summary, ""]
        if plan.weak_subjects:
            lines.append("**Weak subjects to prioritize**")
            for w in plan.weak_subjects:
                res = LEARNING_RESOURCES.get(w["subject"], [])
                res_txt = f" — _Try: {res[0]}_" if res else ""
                lines.append(f"• **{w['subject']}** ({w['score']:.0f}%) — {w['priority']} priority{res_txt}")
            lines.append("")
        for phase in plan.phases:
            lines.append(f"**Week {phase.week}** — {', '.join(phase.subjects)} (~{phase.daily_hours}h/day)")
            for t in phase.tasks:
                lines.append(f"  - {t}")
            lines.append("")
        return "\n".join(lines)
