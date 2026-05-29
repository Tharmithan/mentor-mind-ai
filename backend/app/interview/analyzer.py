"""Answer analysis for mock interviews (Week 5 · Day 1).

Day 1 uses a structured heuristic scorer so the flow works without an LLM.
Later days can swap in LLM-based evaluation via ``OPENAI_API_KEY``.
"""

from __future__ import annotations

import re

from app.interview.question_bank import InterviewQuestion

# Keywords that suggest a strong answer per interview type.
_TYPE_HINTS: dict[str, list[str]] = {
    "hr": ["experience", "skill", "team", "learn", "goal", "company", "role", "passion"],
    "technical": [
        "because", "complexity", "algorithm", "example", "implement", "data",
        "function", "api", "model", "system", "code", "structure",
    ],
    "behavioral": [
        "situation", "task", "action", "result", "team", "learned", "challenge",
        "resolved", "communicat", "led", "helped", "improved",
    ],
}

_STAR_MARKERS = ["situation", "task", "action", "result", "when", "then", "so"]


def analyze_answer(question: InterviewQuestion, answer: str) -> dict:
    """Score an answer and return feedback + dimension scores."""
    text = answer.strip()
    words = text.split()
    word_count = len(words)

    # Dimension scores (0–10)
    length_score = min(10.0, word_count / 8)  # ~80 words → 10
    structure_score = _structure_score(text, question.interview_type)
    relevance_score = _relevance_score(text, question)
    clarity_score = min(10.0, (length_score + structure_score) / 2)

    overall = round((length_score + structure_score + relevance_score + clarity_score) / 4, 1)

    strengths, improvements = _feedback_bullets(
        question, text, word_count, length_score, structure_score, relevance_score
    )

    return {
        "overall_score": overall,
        "communication_score": round(clarity_score, 1),
        "technical_score": round(relevance_score if question.interview_type == "technical" else structure_score, 1),
        "confidence_score": round(min(10.0, length_score * 0.6 + structure_score * 0.4), 1),
        "feedback_summary": _summary(question, overall, strengths, improvements),
        "strengths": strengths,
        "improvements": improvements,
        "word_count": word_count,
    }


def _structure_score(text: str, interview_type: str) -> float:
    lower = text.lower()
    score = 3.0
    if re.search(r"[.!?]", text):
        score += 2.0
    if len(text.split()) >= 40:
        score += 2.0
    if interview_type == "behavioral":
        hits = sum(1 for m in _STAR_MARKERS if m in lower)
        score += min(3.0, hits * 0.8)
    if interview_type == "hr" and any(w in lower for w in ("i am", "i have", "my experience")):
        score += 1.5
    return min(10.0, score)


def _relevance_score(text: str, question: InterviewQuestion) -> float:
    lower = text.lower()
    hints = _TYPE_HINTS.get(question.interview_type, [])
    hits = sum(1 for h in hints if h in lower)
    cat_words = question.category.replace("-", " ").split()
    cat_hits = sum(1 for w in cat_words if w in lower)
    return min(10.0, 4.0 + hits * 0.9 + cat_hits * 1.2)


def _feedback_bullets(
    question: InterviewQuestion,
    text: str,
    word_count: int,
    length_score: float,
    structure_score: float,
    relevance_score: float,
) -> tuple[list[str], list[str]]:
    strengths: list[str] = []
    improvements: list[str] = []

    if word_count >= 50:
        strengths.append("Good answer length — you gave enough detail.")
    else:
        improvements.append("Expand your answer — aim for at least 60–90 seconds of speaking (~80+ words).")

    if structure_score >= 6:
        strengths.append("Answer was well structured with clear sentences.")
    else:
        improvements.append("Use a clearer structure (e.g. STAR for behavioral questions).")

    if relevance_score >= 6:
        strengths.append("Content was relevant to the question asked.")
    else:
        improvements.append(f"Tie your answer more directly to: \"{question.text[:60]}…\"")

    if question.interview_type == "behavioral" and "result" not in text.lower():
        improvements.append("End with a measurable Result (the R in STAR).")

    if not strengths:
        strengths.append("You attempted the question — practice will sharpen delivery.")

    return strengths[:3], improvements[:3]


def _summary(
    question: InterviewQuestion,
    overall: float,
    strengths: list[str],
    improvements: list[str],
) -> str:
    label = "strong" if overall >= 7.5 else "solid" if overall >= 5.5 else "needs work"
    return (
        f"{label.capitalize()} answer ({overall}/10) for a {question.category} question. "
        f"Key strength: {strengths[0] if strengths else 'effort shown'}. "
        f"Focus next: {improvements[0] if improvements else 'keep practicing'}."
    )
