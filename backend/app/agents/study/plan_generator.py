"""Exam study plan generator (Week 6 · Day 2)."""

from __future__ import annotations

import re

from app.agents.study.curricula import (
    CURRICULA,
    DEFAULT_CURRICULUM,
    LEARNING_RESOURCES,
    SUBJECT_ALIASES,
)
from app.models.study_tutor import ExamStudyPlanRequest, ExamStudyPlanResponse, StudyPlanDay
from app.rag.llm import call_llm, llm_enabled, parse_json


def parse_exam_request(message: str) -> tuple[str | None, int | None]:
    """Extract subject and day count from natural language."""
    lower = message.lower()

    days: int | None = None
    for pat in (
        r"(\d+)\s*days?\s*(?:until|before|left|remaining|to go)?",
        r"in\s+(\d+)\s*days?",
        r"(\d+)\s*day\s+(?:study\s+)?plan",
    ):
        m = re.search(pat, lower)
        if m:
            days = int(m.group(1))
            break
    if days is None:
        wm = re.search(r"(\d+)\s*weeks?", lower)
        if wm:
            days = int(wm.group(1)) * 7
    if days is None and "fortnight" in lower:
        days = 14
    if days is None and "two weeks" in lower:
        days = 14
    if days is None and "one week" in lower or "1 week" in lower:
        days = 7

    subject: str | None = None
    for alias, canonical in sorted(SUBJECT_ALIASES.items(), key=lambda x: -len(x[0])):
        if alias in lower:
            subject = canonical
            break
    if subject is None:
        exam_m = re.search(
            r"(?:exam|test|midterm|final)\s+(?:in|on|for)\s+([a-z][a-z\s]{2,30}?)(?:\s+in|\s*$|\.)",
            lower,
        )
        if exam_m:
            raw = exam_m.group(1).strip()
            subject = SUBJECT_ALIASES.get(raw, raw.title())

    return subject, days


def _stretch_curriculum(subject: str, days: int) -> list[tuple[str, str, list[str]]]:
    base = CURRICULA.get(subject, DEFAULT_CURRICULUM)
    if len(base) >= days:
        return base[:days]
    # Repeat later phases with "Review" prefix for longer plans
    out = list(base)
    i = 0
    while len(out) < days:
        phase, focus, tasks = base[i % len(base)]
        out.append((f"Review — {phase}", focus, [f"Review: {t}" for t in tasks]))
        i += 1
    return out[:days]


def _build_schedule(
    subject: str,
    days: int,
    hours_per_day: float,
) -> list[StudyPlanDay]:
    curriculum = _stretch_curriculum(subject, days)
    resources = LEARNING_RESOURCES.get(subject, LEARNING_RESOURCES.get("Programming", []))
    schedule: list[StudyPlanDay] = []
    for i, (phase, focus, tasks) in enumerate(curriculum, start=1):
        schedule.append(
            StudyPlanDay(
                day=i,
                phase=phase,
                focus=focus,
                tasks=tasks,
                duration_hours=hours_per_day,
                resources=resources[:2] if i <= 3 else resources[2:4] if len(resources) > 2 else resources[:1],
            )
        )
    return schedule


def _format_plan_markdown(plan: ExamStudyPlanResponse) -> str:
    lines = [
        f"## {plan.days}-Day {plan.subject} Study Plan",
        "",
        plan.summary,
        "",
        f"**Daily commitment:** ~{plan.hours_per_day}h/day · **Phases:** {', '.join(plan.phases)}",
        "",
    ]
    for day in plan.schedule[: min(7, len(plan.schedule))]:
        tasks = "\n".join(f"  - {t}" for t in day.tasks)
        lines.append(f"**Day {day.day} — {day.phase}: {day.focus}** ({day.duration_hours}h)")
        lines.append(tasks)
        if day.resources:
            lines.append(f"  _Resources: {', '.join(day.resources[:2])}_")
        lines.append("")
    if len(plan.schedule) > 7:
        lines.append(f"_…plus {len(plan.schedule) - 7} more days (see full plan in Dashboard)._")
        lines.append("")
    if plan.tips:
        lines.append("**Tips**")
        for tip in plan.tips:
            lines.append(f"• {tip}")
    return "\n".join(lines)


class StudyPlanGenerator:
    @staticmethod
    async def generate(req: ExamStudyPlanRequest) -> ExamStudyPlanResponse:
        subject = req.subject.strip().title()
        for alias, canonical in SUBJECT_ALIASES.items():
            if alias == req.subject.lower():
                subject = canonical
                break

        schedule = _build_schedule(subject, req.days, req.hours_per_day)
        phases = list(dict.fromkeys(d.phase for d in schedule))
        resources = LEARNING_RESOURCES.get(subject, [])
        tips = [
            f"Block {req.hours_per_day}h daily — consistency beats cramming.",
            "End each session with 5 flashcards from that day's topics.",
            "Do one timed practice set in the final 3 days before the exam.",
        ]
        if resources:
            tips.append(f"Primary resource: {resources[0]}")

        summary = (
            f"Personalized **{req.days}-day** plan for **{subject}**. "
            f"Week 1 builds foundations; middle days cover core topics; "
            f"the final days focus on practice exams and light review."
        )

        used_llm = False
        if llm_enabled() and subject not in CURRICULA:
            enhanced = await StudyPlanGenerator._llm_enhance(subject, req.days, schedule)
            if enhanced:
                schedule = enhanced
                used_llm = True
                summary = (
                    f"AI-customized **{req.days}-day** plan for **{subject}** "
                    f"with daily tasks tuned to your timeline."
                )

        return ExamStudyPlanResponse(
            subject=subject,
            days=req.days,
            hours_per_day=req.hours_per_day,
            summary=summary,
            phases=phases,
            schedule=schedule,
            tips=tips,
            used_llm=used_llm,
        )

    @staticmethod
    async def from_message(message: str, hours_per_day: float = 2.0) -> ExamStudyPlanResponse | None:
        subject, days = parse_exam_request(message)
        if not subject and not days:
            if not re.search(r"\b(exam|study plan|prepare for)\b", message.lower()):
                return None
        subject = subject or "General"
        days = days or 14
        return await StudyPlanGenerator.generate(
            ExamStudyPlanRequest(subject=subject, days=days, hours_per_day=hours_per_day)
        )

    @staticmethod
    async def _llm_enhance(
        subject: str,
        days: int,
        schedule: list[StudyPlanDay],
    ) -> list[StudyPlanDay] | None:
        sample = [{"day": d.day, "focus": d.focus, "tasks": d.tasks} for d in schedule[:5]]
        prompt = (
            f"Create a {days}-day exam study plan for {subject}. "
            f"Respond JSON: {{\"days\":[{{\"day\":1,\"phase\":\"...\",\"focus\":\"...\","
            f"\"tasks\":[\"...\"],\"duration_hours\":2}}]}}\n"
            f"Sample structure: {sample}"
        )
        raw = await call_llm(
            [
                {"role": "system", "content": "Output valid JSON only. Be specific and practical."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1200,
            force_json=True,
        )
        data = parse_json(raw)
        if not data or not data.get("days"):
            return None
        out: list[StudyPlanDay] = []
        for item in data["days"][:days]:
            out.append(
                StudyPlanDay(
                    day=int(item.get("day", len(out) + 1)),
                    phase=str(item.get("phase", "Study")),
                    focus=str(item.get("focus", subject)),
                    tasks=[str(t) for t in item.get("tasks", [])][:4],
                    duration_hours=float(item.get("duration_hours", 2.0)),
                    resources=LEARNING_RESOURCES.get(subject, [])[:2],
                )
            )
        return out or None

    @staticmethod
    def to_markdown(plan: ExamStudyPlanResponse) -> str:
        return _format_plan_markdown(plan)
