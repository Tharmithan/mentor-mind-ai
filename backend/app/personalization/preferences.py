"""Learning preference tracking and style inference (Week 7 · Day 1)."""

from __future__ import annotations

from datetime import datetime, timezone

from app.models.personalization import LearningPreferences, LearningStyle

STYLE_KEYWORDS: dict[LearningStyle, list[str]] = {
    "video": ["video", "youtube", "watch", "lecture", "visual", "course video"],
    "reading": ["read", "pdf", "book", "documentation", "docs", "notes", "textbook"],
    "interactive": ["quiz", "flashcard", "practice", "exercise", "leetcode", "duolingo"],
    "hands_on": ["project", "build", "lab", "github", "kaggle", "portfolio", "code"],
}

STYLE_DEFAULT_FORMATS: dict[LearningStyle, list[str]] = {
    "video": ["YouTube tutorials", "Video lectures", "Interactive video courses"],
    "reading": ["PDF textbooks", "Official documentation", "Structured notes"],
    "interactive": ["Interactive quizzes", "Flashcards", "Coding challenges"],
    "hands_on": ["Mini projects", "GitHub repos", "Kaggle notebooks"],
}


class LearningPreferenceTracker:
    @staticmethod
    def infer_from_text(message: str) -> dict[str, float]:
        """Boost style scores from natural language signals."""
        lower = message.lower()
        scores = {k: 0.0 for k in STYLE_KEYWORDS}
        for style, keywords in STYLE_KEYWORDS.items():
            for kw in keywords:
                if kw in lower:
                    scores[style] += 1.0
        total = sum(scores.values()) or 1.0
        return {k: round(v / total, 3) for k, v in scores.items()}

    @staticmethod
    def merge_preferences(
        current: LearningPreferences,
        inferred: dict[str, float] | None = None,
        explicit_style: LearningStyle | None = None,
    ) -> LearningPreferences:
        scores = dict(current.style_scores)
        if inferred:
            for style, weight in inferred.items():
                scores[style] = round(scores.get(style, 0.25) * 0.6 + weight * 0.4, 3)
        if explicit_style:
            for k in scores:
                scores[k] = round(scores[k] * 0.7, 3)
            scores[explicit_style] = round(scores.get(explicit_style, 0) + 0.3, 3)
        primary = max(scores, key=scores.get)  # type: ignore[arg-type]
        return LearningPreferences(
            primary_style=explicit_style or primary,
            style_scores=scores,
            preferred_session_minutes=current.preferred_session_minutes,
            preferred_study_time=current.preferred_study_time,
            content_formats=STYLE_DEFAULT_FORMATS.get(primary, []),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

    @staticmethod
    def rationale(style: LearningStyle) -> str:
        examples = {
            "video": "You learn best through videos — we'll prioritize YouTube tutorials and visual courses.",
            "reading": "You learn best through reading — we'll prioritize PDFs, docs, and structured notes.",
            "interactive": "You learn best interactively — we'll prioritize quizzes and hands-on exercises.",
            "hands_on": "You learn best by building — we'll prioritize projects and practical labs.",
        }
        return examples.get(style, "Recommendations adapt to your learning style.")
