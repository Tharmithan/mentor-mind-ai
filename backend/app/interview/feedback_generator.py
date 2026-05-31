"""Human-like interview feedback + post-session coach (Week 5 · Day 4)."""

from __future__ import annotations

import json
import os
import re
from typing import TYPE_CHECKING

import httpx

from app.config import settings
from app.interview.question_bank import InterviewQuestion, get_question_bank

if TYPE_CHECKING:
    from app.interview.session import InterviewSession, TurnRecord


async def _llm_json(prompt: str, max_tokens: int = 800) -> dict | None:
    api_key = os.getenv("OPENAI_API_KEY") or getattr(settings, "openai_api_key", None)
    if not api_key:
        return None
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are a supportive interview coach. Write clear, encouraging "
                                "feedback in second person. Output valid JSON only."
                            ),
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.5,
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            return json.loads(resp.json()["choices"][0]["message"]["content"])
    except Exception:
        return None


def _has_fillers(text: str) -> bool:
    return bool(re.search(r"\b(um|uh|like|you know|sort of|kind of)\b", text, re.I))


async def generate_turn_feedback(
    question: InterviewQuestion,
    answer: str,
    analysis: dict,
) -> dict:
    """Rich per-answer feedback: human sentences, strengths, weaknesses, suggestions."""
    scores = analysis.get("scores") or {}
    ideal = analysis.get("ideal_comparison") or {}
    llm = await _llm_json(
        (
            "Generate interview feedback for one answer.\n"
            "JSON keys:\n"
            '  "human_feedback": array of 2-3 complete sentences (natural coach tone),\n'
            '  "strengths": array of 2 strings,\n'
            '  "weaknesses": array of 2 strings,\n'
            '  "improvement_suggestions": array of 2-3 actionable tips '
            "(include delivery: eye contact, filler words, pacing when relevant)\n\n"
            f"INTERVIEW TYPE: {question.interview_type}\n"
            f"QUESTION: {question.text}\n"
            f"ANSWER: {answer}\n"
            f"SCORES: {json.dumps(scores)}\n"
            f"MISSING KEYWORDS: {ideal.get('missing_keywords', [])}\n"
            f"SIMILARITY TO IDEAL: {ideal.get('similarity_pct', 'n/a')}%"
        ),
        max_tokens=500,
    )
    if llm:
        return {
            "human_feedback": list(llm.get("human_feedback", []))[:4],
            "strengths": list(llm.get("strengths", analysis.get("strengths", [])))[:3],
            "weaknesses": list(llm.get("weaknesses", []))[:3],
            "improvement_suggestions": list(llm.get("improvement_suggestions", []))[:4],
            "used_llm": True,
        }

    return _heuristic_turn_feedback(question, answer, analysis)


def _heuristic_turn_feedback(
    question: InterviewQuestion,
    answer: str,
    analysis: dict,
) -> dict:
    scores = analysis.get("scores") or {}
    ideal = analysis.get("ideal_comparison") or {}
    missing = ideal.get("missing_keywords") or []
    overall = scores.get("overall", int(analysis.get("overall_score", 5) * 10))
    technical = scores.get("technical_score", int(analysis.get("technical_score", 5) * 10))
    comm = scores.get("communication", int(analysis.get("communication_score", 5) * 10))

    human: list[str] = []
    weaknesses: list[str] = []
    suggestions: list[str] = list(analysis.get("improvements", []))[:2]

    if technical >= 70 and comm < 65:
        human.append(
            "Your answer was technically on track, but it would land better with a concrete "
            "real-world example and a clearer opening line."
        )
        weaknesses.append("Limited real-world examples to back up your points.")
    elif technical < 60 and comm >= 65:
        human.append(
            "You communicated clearly, but the content did not fully address what the interviewer "
            "was probing for — deepen the technical or situational detail."
        )
        weaknesses.append("Answer drifted from the core of the question.")
    elif overall >= 75:
        human.append(
            "Strong response — you stayed on topic and showed good structure. "
            "Polish delivery to make it interview-ready."
        )
    else:
        human.append(
            "You made a solid attempt. Tighten structure and add one specific example "
            "to move this from good to great."
        )
        weaknesses.append("Structure and specificity need more work.")

    if _has_fillers(answer):
        human.append(
            "Try reducing filler words (um, like) and pausing briefly instead — "
            "it will sound more confident."
        )
        weaknesses.append("Frequent filler words reduced perceived confidence.")
        suggestions.append("Practice answers out loud and pause instead of using filler words.")

    if missing:
        human.append(
            f"Consider weaving in concepts like: {', '.join(missing[:4])}."
        )
        weaknesses.append(f"Did not mention key ideas: {', '.join(missing[:3])}.")

    if len(answer.split()) < 40:
        suggestions.append("Aim for 60–90 seconds — expand with context, action, and outcome.")
        weaknesses.append("Answer was shorter than a typical interview response.")

    suggestions.append(
        "Maintain eye contact with the camera and smile at the start and end of each answer."
    )

    strengths = list(analysis.get("strengths", []))[:3]
    if not weaknesses:
        weaknesses.append("Room to add more measurable outcomes or metrics.")

    if not human:
        human.append(analysis.get("feedback_summary", "Keep practicing — you're building momentum."))

    return {
        "human_feedback": human[:4],
        "strengths": strengths,
        "weaknesses": weaknesses[:3],
        "improvement_suggestions": list(dict.fromkeys(suggestions))[:4],
        "used_llm": False,
    }


async def generate_coach_report(session: "InterviewSession") -> dict:
    """Post-interview AI coach: roadmap, topics, practice questions."""
    turns = session.turns
    if not turns:
        return {}

    turns_blob = []
    for t in turns:
        turns_blob.append(
            {
                "question": t.question_text,
                "answer_preview": t.answer_text[:300],
                "scores": t.scores,
                "strengths": t.strengths,
                "weaknesses": getattr(t, "weaknesses", []),
            }
        )

    llm = await _llm_json(
        (
            "Create a post-interview coaching plan.\n"
            "JSON keys:\n"
            '  "overview": string (2-3 encouraging sentences),\n'
            '  "strengths": array of 3 strings,\n'
            '  "weaknesses": array of 3 strings,\n'
            '  "improvement_roadmap": array of 3-5 objects '
            '{ "phase": string, "focus": string, "actions": array of strings },\n'
            '  "learning_topics": array of 5 strings,\n'
            '  "practice_questions": array of 3 objects '
            '{ "question": string, "category": string, "reason": string }\n\n'
            f"INTERVIEW TYPE: {session.interview_type}\n"
            f"TURNS: {json.dumps(turns_blob)}"
        ),
        max_tokens=900,
    )
    if llm:
        return {
            "overview": str(llm.get("overview", "")),
            "strengths": list(llm.get("strengths", []))[:5],
            "weaknesses": list(llm.get("weaknesses", []))[:5],
            "improvement_roadmap": list(llm.get("improvement_roadmap", []))[:5],
            "learning_topics": list(llm.get("learning_topics", []))[:8],
            "practice_questions": list(llm.get("practice_questions", []))[:5],
            "used_llm": True,
        }

    return _heuristic_coach_report(session)


def _heuristic_coach_report(session: "InterviewSession") -> dict:
    bank = get_question_bank()
    itype = session.interview_type
    extra = bank.pick(itype, 3)

    all_weak: list[str] = []
    all_str: list[str] = []
    low_comm = low_tech = 0
    for t in session.turns:
        all_str.extend(t.strengths[:1])
        all_weak.extend(getattr(t, "weaknesses", [])[:1])
        sc = t.scores or {}
        if sc.get("communication", 70) < 65:
            low_comm += 1
        if sc.get("technical_score", 70) < 65:
            low_tech += 1

    topics_map = {
        "hr": ["STAR storytelling", "Company research", "Salary & role fit", "Elevator pitch", "Weakness framing"],
        "technical": ["Data structures", "System design basics", "Complexity analysis", "Debugging stories", "API design"],
        "behavioral": ["STAR method", "Conflict resolution", "Leadership examples", "Team collaboration", "Growth mindset"],
    }
    topics = topics_map.get(itype, topics_map["hr"])

    roadmap = [
        {
            "phase": "Week 1",
            "focus": "Structure & clarity",
            "actions": [
                "Record 3 mock answers and review filler words",
                "Use STAR for every behavioral answer",
            ],
        },
        {
            "phase": "Week 2",
            "focus": "Depth & examples",
            "actions": [
                "Add one real project example per technical answer",
                "Practice 60–90 second timed responses",
            ],
        },
        {
            "phase": "Week 3",
            "focus": "Delivery",
            "actions": [
                "Mock interview on camera — check eye contact",
                "Redo your weakest 2 questions from this session",
            ],
        },
    ]

    if low_comm >= 2:
        roadmap[0]["actions"].insert(0, "Daily 5-minute speaking drills — slow pace, clear endings")

    practice = [
        {
            "question": q.text,
            "category": q.category,
            "reason": f"Targets {q.category} — an area to strengthen from this session.",
        }
        for q in extra
    ]

    avg = session.summary()
    score_line = f"{avg['overall_score']}/10" if avg else "N/A"

    return {
        "overview": (
            f"You completed a {itype} mock interview ({score_line} average). "
            "Focus on consistent structure, concrete examples, and calm delivery — "
            "you're closer to interview-ready than you think."
        ),
        "strengths": list(dict.fromkeys(all_str))[:5] or ["Showed up and answered every question"],
        "weaknesses": list(dict.fromkeys(all_weak))[:5] or ["Add more specific examples"],
        "improvement_roadmap": roadmap,
        "learning_topics": topics,
        "practice_questions": practice,
        "used_llm": False,
    }
