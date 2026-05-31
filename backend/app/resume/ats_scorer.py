"""ATS compatibility scoring heuristics (Week 6 · Day 4)."""

from __future__ import annotations

import re

from app.models.resume import ATSCheckItem

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s\-().]{7,}\d)")
LINKEDIN_RE = re.compile(r"linkedin\.com", re.I)
GITHUB_RE = re.compile(r"github\.com", re.I)
METRIC_RE = re.compile(
    r"\b\d+\s*%|\b\d+\+?\s*(users|customers|projects|hours|ms|seconds|x|k\b|m\b)|"
    r"\$\d+|\b(increased|decreased|reduced|improved|saved|grew)\s+(by\s+)?\d+",
    re.I,
)


def score_ats(text: str, sections: list) -> tuple[float, str, list[ATSCheckItem]]:
    checks: list[ATSCheckItem] = []
    lower = text.lower()
    section_names = {s.name.lower() for s in sections}

    # Contact information
    has_email = bool(EMAIL_RE.search(text))
    has_phone = bool(PHONE_RE.search(text))
    contact_score = 10 if has_email else 0
    if has_phone:
        contact_score = min(10, contact_score + 3)
    checks.append(
        ATSCheckItem(
            category="contact",
            label="Contact information",
            passed=has_email,
            score=contact_score,
            detail="Email found" if has_email else "Add a professional email address",
        )
    )

    # Standard sections
    expected = {"experience", "education", "skills"}
    found = sum(
        1
        for e in expected
        if any(e in name for name in section_names)
        or e in lower[:2000]
    )
    section_score = min(10, found * 3.5)
    checks.append(
        ATSCheckItem(
            category="structure",
            label="Standard sections",
            passed=found >= 2,
            score=section_score,
            detail=f"Found {found}/3 core sections (Experience, Education, Skills)",
        )
    )

    # Keywords / parsability
    special_ratio = len(re.findall(r"[^\w\s@.\-+%,/()#]", text)) / max(len(text), 1)
    parsable = special_ratio < 0.08
    parse_score = 10 if parsable else max(3, 10 - special_ratio * 100)
    checks.append(
        ATSCheckItem(
            category="formatting",
            label="ATS-friendly characters",
            passed=parsable,
            score=parse_score,
            detail="Low special-character density — good for ATS parsers"
            if parsable
            else "Reduce symbols, tables, or decorative characters",
        )
    )

    # Action verbs & metrics
    from app.resume.parser import STRONG_VERBS, extract_bullets

    bullets = extract_bullets(text)
    strong_count = sum(1 for b in bullets if any(v in b.lower() for v in STRONG_VERBS))
    metric_count = sum(1 for b in bullets if METRIC_RE.search(b))
    verb_score = min(10, (strong_count / max(len(bullets), 1)) * 12)
    checks.append(
        ATSCheckItem(
            category="content",
            label="Strong action verbs",
            passed=strong_count >= 2,
            score=round(verb_score, 1),
            detail=f"{strong_count} bullets start with strong verbs",
        )
    )
    metric_score = min(10, metric_count * 2.5)
    checks.append(
        ATSCheckItem(
            category="content",
            label="Quantified achievements",
            passed=metric_count >= 2,
            score=round(metric_score, 1),
            detail=f"{metric_count} bullets include metrics (%, numbers, impact)",
        )
    )

    # Online presence
    has_link = bool(LINKEDIN_RE.search(text) or GITHUB_RE.search(text))
    checks.append(
        ATSCheckItem(
            category="contact",
            label="LinkedIn / GitHub",
            passed=has_link,
            score=8 if has_link else 4,
            detail="Professional links found" if has_link else "Add LinkedIn or GitHub URL",
        )
    )

    # Length
    words = len(text.split())
    length_ok = 250 <= words <= 900
    length_score = 10 if length_ok else 6 if words >= 150 else 3
    checks.append(
        ATSCheckItem(
            category="formatting",
            label="Resume length",
            passed=length_ok,
            score=length_score,
            detail=f"~{words} words — {'ideal for early career' if length_ok else 'aim for 1 page (~400–700 words)'}",
        )
    )

    total = sum(c.score for c in checks)
    max_score = len(checks) * 10
    pct = round(total / max_score * 100, 1)
    grade = "A" if pct >= 85 else "B" if pct >= 70 else "C" if pct >= 55 else "D"
    return pct, grade, checks
