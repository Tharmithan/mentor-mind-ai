"""AI feedback generation for resume analysis (Week 6 · Day 4)."""

from __future__ import annotations

from app.models.resume import (
    ATSCheckItem,
    MissingSkill,
    ResumeFeedbackItem,
    WeakBullet,
)
from app.rag.llm import call_llm, llm_enabled, parse_json


async def generate_ai_feedback(
    text: str,
    ats_score: float,
    ats_checks: list[ATSCheckItem],
    missing_skills: list[MissingSkill],
    weak_bullets: list[WeakBullet],
    formatting_issues: list[str],
    target_role: str | None = None,
) -> tuple[str, str, list[ResumeFeedbackItem], bool]:
    """Return (headline, summary, feedback_items, used_llm)."""
    fallback_headline, fallback_summary, fallback_items = _heuristic_feedback(
        ats_score, missing_skills, weak_bullets, formatting_issues
    )

    if not llm_enabled():
        return fallback_headline, fallback_summary, fallback_items, False

    failed = [c.label for c in ats_checks if not c.passed]
    gaps = [m.skill for m in missing_skills[:5]]
    weak = [w.issue for w in weak_bullets[:3]]

    prompt = (
        f"Analyze this resume for a student targeting {target_role or 'tech'} roles.\n"
        f"ATS score: {ats_score}/100. Failed checks: {failed}. Missing skills: {gaps}. "
        f"Weak bullets: {weak}. Formatting: {formatting_issues}.\n\n"
        "Respond JSON:\n"
        '{"headline":"one punchy line","summary":"2-3 sentences",'
        '"feedback":[{"category":"skills|ats|formatting|content","priority":"high|medium|low",'
        '"message":"specific actionable tip"}]}\n\n'
        f"RESUME (excerpt):\n{text[:3500]}"
    )
    raw = await call_llm(
        [
            {"role": "system", "content": "Expert resume coach. Output valid JSON only. Be specific."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=700,
        force_json=True,
    )
    data = parse_json(raw)
    if not data:
        return fallback_headline, fallback_summary, fallback_items, False

    items = [
        ResumeFeedbackItem(
            category=str(f.get("category", "content")),
            priority=str(f.get("priority", "medium")),
            message=str(f.get("message", "")),
        )
        for f in data.get("feedback", [])
        if f.get("message")
    ][:8]
    if not items:
        items = fallback_items

    return (
        str(data.get("headline", fallback_headline)),
        str(data.get("summary", fallback_summary)),
        items,
        True,
    )


def _heuristic_feedback(
    ats_score: float,
    missing_skills: list[MissingSkill],
    weak_bullets: list[WeakBullet],
    formatting_issues: list[str],
) -> tuple[str, str, list[ResumeFeedbackItem]]:
    items: list[ResumeFeedbackItem] = []

    if missing_skills:
        top = missing_skills[0]
        items.append(
            ResumeFeedbackItem(
                category="skills",
                priority="high",
                message=f"Add **{top.skill}** — {top.suggestion}",
            )
        )

    if weak_bullets:
        items.append(
            ResumeFeedbackItem(
                category="content",
                priority="high",
                message=weak_bullets[0].suggestion,
            )
        )

    if ats_score < 70:
        items.append(
            ResumeFeedbackItem(
                category="ats",
                priority="high",
                message="Improve ATS compatibility: use standard section headers and add quantified bullet points.",
            )
        )

    for issue in formatting_issues[:2]:
        items.append(
            ResumeFeedbackItem(
                category="formatting",
                priority="medium",
                message=issue,
            )
        )

    if not items:
        items.append(
            ResumeFeedbackItem(
                category="content",
                priority="medium",
                message="Add more AI project metrics and technical achievements to stand out to recruiters.",
            )
        )

    headline = (
        "Strong foundation — add metrics and missing skills to impress recruiters."
        if ats_score >= 70
        else "Good start — focus on ATS formatting and quantified impact."
    )
    summary = (
        f"Your resume scores **{ats_score:.0f}/100** on ATS compatibility. "
        f"{len(missing_skills)} skill gaps and {len(weak_bullets)} weak descriptions identified."
    )
    return headline, summary, items
