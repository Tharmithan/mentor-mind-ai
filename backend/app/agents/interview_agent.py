"""Interview Agent — mock interview coaching (Week 6 · Day 1)."""

from __future__ import annotations

import re

from app.interview.service import InterviewService
from app.interview.types import INTERVIEW_TYPE_META, InterviewType
from app.rag.llm import call_llm, llm_enabled


async def run_interview_agent(
    message: str,
    session_id: str | None,
    interview_session_id: str | None,
    context: dict,
) -> dict:
    lower = message.lower()

    if re.search(r"\b(start|begin|practice)\b.*\b(interview|mock)\b", lower) or re.search(
        r"\b(hr|technical|behavioral)\s+interview\b", lower
    ):
        itype = "technical"
        if "hr" in lower:
            itype = "hr"
        elif "behavior" in lower:
            itype = "behavioral"
        try:
            res = InterviewService.start(itype, num_questions=5)
            q = res.current_question
            label = INTERVIEW_TYPE_META[InterviewType(itype)]["label"]
            answer = (
                f"**{label}** session started ({res.total_questions} questions).\n\n"
                f"**Q1:** {q.text}\n\n"
                f"_Tip: {q.tips}_\n\n"
                f"Open [/interview](/interview) to use voice + live confidence tracking."
            )
            return {
                "answer": answer,
                "used_llm": False,
                "sub_intent": "start_interview",
                "actions": [
                    {"type": "navigate", "path": "/interview"},
                    {"type": "interview_session", "session_id": res.session_id},
                ],
                "data": {"interview_session_id": res.session_id},
            }
        except Exception as exc:
            return {"answer": f"Could not start interview: {exc}", "used_llm": False, "sub_intent": "error"}

    if interview_session_id or context.get("interview_session_id"):
        iid = interview_session_id or context.get("interview_session_id")
        try:
            report = await InterviewService.get_coach_report(iid)
            answer = (
                f"**Interview coach summary**\n\n{report.overview}\n\n"
                f"**Next steps:** {report.improvement_roadmap[0].actions[0] if report.improvement_roadmap else 'Practice again'}"
            )
            return {
                "answer": answer,
                "used_llm": report.used_llm,
                "sub_intent": "coach_report",
                "actions": [{"type": "navigate", "path": "/interview"}],
            }
        except Exception:
            pass

    # Coaching tips via LLM or template
    if llm_enabled():
        raw = await call_llm(
            [
                {
                    "role": "system",
                    "content": "You are an expert interview coach. Give concise, actionable advice.",
                },
                {"role": "user", "content": message},
            ],
            max_tokens=400,
        )
        if raw:
            return {
                "answer": raw,
                "used_llm": True,
                "sub_intent": "coaching",
                "actions": [{"type": "navigate", "path": "/interview"}],
            }

    types_list = ", ".join(m["label"] for m in INTERVIEW_TYPE_META.values())
    answer = (
        "I can help you prepare for interviews.\n\n"
        f"• **Start a mock interview** — say \"start a technical interview\"\n"
        f"• Available types: {types_list}\n"
        "• Use the [Interview Coach](/interview) for voice answers + AI feedback\n\n"
        f"For your question: _{message[:80]}…_ — focus on STAR for behavioral Qs and "
        "concrete examples for technical ones."
    )
    return {
        "answer": answer,
        "used_llm": False,
        "sub_intent": "coaching",
        "actions": [{"type": "navigate", "path": "/interview"}],
    }
