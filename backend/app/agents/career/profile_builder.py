"""Build unified student career profile from performance + interviews (Week 6 · Day 3)."""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.agents.career.paths import SUBJECT_SKILL_MAP
from app.models.career import StudentCareerProfile
from app.recommendation.engine import StudentProfile, get_recommendation_engine

INTERVIEW_DIR = Path(__file__).resolve().parents[3] / "uploads" / "interview_sessions"

INTEREST_KEYWORDS: dict[str, list[str]] = {
    "ai": ["ai", "artificial intelligence", "llm", "genai", "gpt"],
    "ml": ["machine learning", "ml", "deep learning", "neural"],
    "data": ["data science", "data scientist", "analytics", "statistics"],
    "software": ["software", "web dev", "backend", "frontend", "full stack"],
    "mlops": ["mlops", "devops", "deploy", "kubernetes", "cloud"],
}


def parse_interests(message: str | None, explicit: list[str] | None = None) -> list[str]:
    found: list[str] = list(explicit or [])
    if not message:
        return found
    lower = message.lower()
    for interest, keywords in INTEREST_KEYWORDS.items():
        if any(k in lower for k in keywords) and interest not in found:
            found.append(interest)
    return found


def _load_interview_averages(session_id: str | None = None) -> dict[str, float | None]:
    """Average interview scores from one session or all completed sessions."""
    if not INTERVIEW_DIR.exists():
        return {
            "overall": None,
            "technical": None,
            "communication": None,
            "confidence": None,
        }

    sessions: list[dict] = []
    if session_id:
        path = INTERVIEW_DIR / f"{session_id}.json"
        if path.exists():
            sessions.append(json.loads(path.read_text(encoding="utf-8")))
    else:
        for path in sorted(INTERVIEW_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]:
            try:
                sessions.append(json.loads(path.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                continue

    if not sessions:
        return {"overall": None, "technical": None, "communication": None, "confidence": None}

    totals = {"overall": 0.0, "technical": 0.0, "communication": 0.0, "confidence": 0.0}
    counts = {k: 0 for k in totals}

    for sess in sessions:
        turns = sess.get("turns") or []
        for t in turns:
            for key, field in (
                ("overall", "overall_score"),
                ("technical", "technical_score"),
                ("communication", "communication_score"),
                ("confidence", "confidence_score"),
            ):
                val = t.get(field)
                if val is not None:
                    totals[key] += float(val)
                    counts[key] += 1
        # Completed session summary
        summary = sess.get("summary") or {}
        if summary.get("average_overall") is not None and not turns:
            totals["overall"] += float(summary["average_overall"])
            counts["overall"] += 1

    return {
        k: round(totals[k] / counts[k], 1) if counts[k] else None
        for k in totals
    }


def _derive_skills(subject_scores: dict[str, float], interview: dict[str, float | None]) -> dict[str, float]:
    skills: dict[str, float] = {}
    for subject, score in subject_scores.items():
        for skill in SUBJECT_SKILL_MAP.get(subject, []):
            skills[skill] = max(skills.get(skill, 0), score)

    # Interview boosts (scores are 0-10, scale to 0-100)
    if interview.get("technical") is not None:
        tech = float(interview["technical"]) * 10
        skills["programming"] = max(skills.get("programming", 0), tech)
        skills["machine_learning"] = max(skills.get("machine_learning", 0), tech * 0.9)
        skills["algorithms"] = max(skills.get("algorithms", 0), tech * 0.85)
    if interview.get("communication") is not None:
        comm = float(interview["communication"]) * 10
        skills["communication"] = max(skills.get("communication", 0), comm)
    if interview.get("confidence") is not None:
        conf = float(interview["confidence"]) * 10
        skills["communication"] = max(skills.get("communication", 0), conf * 0.85)

    # Baseline ML/AI from programming + math
    prog = skills.get("python", skills.get("programming", 0))
    stats = skills.get("statistics", subject_scores.get("Mathematics", 0))
    skills.setdefault("machine_learning", (prog * 0.6 + stats * 0.4))
    skills.setdefault("deep_learning", skills["machine_learning"] * 0.85)
    skills.setdefault("python", prog or subject_scores.get("Programming", 70))
    skills.setdefault("devops", prog * 0.65)
    skills.setdefault("cloud", prog * 0.6)
    skills.setdefault("nlp", skills.get("machine_learning", 0) * 0.8)
    skills.setdefault("data_visualization", stats * 0.75)
    skills.setdefault("databases", prog * 0.7)
    skills.setdefault("monitoring", skills.get("devops", 0) * 0.8)
    skills.setdefault("software_design", prog * 0.85)
    skills.setdefault("problem_solving", max(
        skills.get("algorithms", 0),
        subject_scores.get("Data Structures", 0),
    ))

    return {k: round(min(100, max(0, v)), 1) for k, v in skills.items()}


class ProfileBuilder:
    @staticmethod
    def build(
        message: str | None = None,
        interests: list[str] | None = None,
        subject_scores: dict[str, float] | None = None,
        interview_session_id: str | None = None,
    ) -> StudentCareerProfile:
        engine = get_recommendation_engine()
        profile = engine.normalize_profile(
            StudentProfile(subject_scores=subject_scores or {})
        )
        scores = profile.subject_scores
        performance = float(sum(scores.values()) / len(scores)) if scores else 70.0

        interview = _load_interview_averages(interview_session_id)
        parsed_interests = parse_interests(message, interests)
        skills = _derive_skills(scores, interview)

        return StudentCareerProfile(
            subject_scores=scores,
            performance_score=round(performance, 1),
            interview_overall=interview["overall"],
            interview_technical=interview["technical"],
            interview_communication=interview["communication"],
            interview_confidence=interview["confidence"],
            interests=parsed_interests,
            skills=skills,
        )


def resolve_career_id(name: str | None) -> str | None:
    if not name:
        return None
    lower = name.lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "data_scientist": "data_scientist",
        "data_science": "data_scientist",
        "datascience": "data_scientist",
        "ai_engineer": "ai_engineer",
        "ai": "ai_engineer",
        "mlops_engineer": "mlops_engineer",
        "mlops": "mlops_engineer",
        "software_engineer": "software_engineer",
        "software": "software_engineer",
        "swe": "software_engineer",
    }
    for key, cid in aliases.items():
        if key in lower:
            return cid
    return None
