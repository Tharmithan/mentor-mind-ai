"""User progress tracking and month-over-month deltas (Week 7 · Day 2)."""

from __future__ import annotations

from datetime import datetime, timezone

from app.models.long_term_memory import LongTermMemory, ProgressDelta, SubjectSnapshot


class ProgressTracker:
    @staticmethod
    def seed_baseline_if_empty(memory: LongTermMemory, current_scores: dict[str, float]) -> None:
        """Seed a 'last month' snapshot for demo progress narratives."""
        if memory.subject_snapshots:
            return
        now = datetime.now(timezone.utc)
        last_month = now.replace(day=1)
        if last_month.month == 1:
            prev = last_month.replace(year=last_month.year - 1, month=12)
        else:
            prev = last_month.replace(month=last_month.month - 1)

        baseline = dict(current_scores)
        # Simulate last-month struggle on ML-related subjects
        for key in list(baseline.keys()):
            if key in ("Programming", "Machine Learning", "Mathematics"):
                baseline[key] = max(45, baseline[key] - 15)
        if "Machine Learning" not in baseline and "Programming" in baseline:
            baseline["Machine Learning"] = max(48, baseline["Programming"] - 18)

        memory.subject_snapshots.append(
            SubjectSnapshot(
                month=prev.strftime("%Y-%m"),
                label=f"{prev.strftime('%B %Y')} (baseline)",
                scores=baseline,
                recorded_at=prev.isoformat(),
            )
        )

    @staticmethod
    def record_snapshot(
        memory: LongTermMemory,
        scores: dict[str, float],
        label: str | None = None,
    ) -> SubjectSnapshot:
        now = datetime.now(timezone.utc)
        month = now.strftime("%Y-%m")
        snap = SubjectSnapshot(
            month=month,
            label=label or now.strftime("Week of %b %d, %Y"),
            scores=dict(scores),
            recorded_at=now.isoformat(),
        )
        # Replace same-month snapshot
        memory.subject_snapshots = [s for s in memory.subject_snapshots if s.month != month]
        memory.subject_snapshots.append(snap)
        memory.subject_snapshots = memory.subject_snapshots[-12:]
        return snap

    @staticmethod
    def enrich_scores(
        scores: dict[str, float],
        baseline: dict[str, float] | None = None,
    ) -> dict[str, float]:
        """Ensure ML subject exists for progress narratives."""
        out = dict(scores)
        if "Machine Learning" not in out:
            base_ml = (baseline or {}).get("Machine Learning", 48)
            out["Machine Learning"] = round(base_ml * 1.15, 1)
        return out

    @staticmethod
    def compute_deltas(
        memory: LongTermMemory,
        current_scores: dict[str, float],
    ) -> list[ProgressDelta]:
        if not memory.subject_snapshots:
            return []

        baseline = memory.subject_snapshots[0]
        period = baseline.label or baseline.month
        current = ProgressTracker.enrich_scores(current_scores, baseline.scores)
        deltas: list[ProgressDelta] = []
        all_subjects = set(baseline.scores) | set(current)
        for subject in sorted(all_subjects):
            prev = baseline.scores.get(subject)
            curr = current.get(subject)
            if prev is None or curr is None:
                continue
            delta = round(curr - prev, 1)
            delta_pct = round((delta / prev) * 100, 1) if prev else 0.0
            insight = ProgressTracker._insight(subject, prev, curr, delta, delta_pct, period)
            deltas.append(
                ProgressDelta(
                    subject=subject,
                    previous_score=prev,
                    current_score=curr,
                    delta=delta,
                    delta_pct=delta_pct,
                    period_label=period,
                    insight=insight,
                )
            )
        deltas.sort(key=lambda d: -abs(d.delta))
        return deltas

    @staticmethod
    def _insight(subject: str, prev: float, curr: float, delta: float, delta_pct: float, period: str) -> str:
        if delta_pct >= 10:
            return f"Your **{subject}** performance improved by **{delta_pct:.0f}%** since {period}."
        if delta >= 10:
            return f"Your **{subject}** performance improved by **{delta_pct:.0f}%** since {period}."
        if delta >= 5:
            return f"**{subject}** is trending up (+{delta:.0f} points) since {period}."
        if delta <= -10:
            return f"**{subject}** dropped {abs(delta_pct):.0f}% since {period} — schedule focused review."
        if delta <= -5:
            return f"**{subject}** needs attention ({delta:.0f} points since {period})."
        if prev < 70 and curr >= 70:
            return f"You crossed the proficiency threshold in **{subject}** (was {prev:.0f}%, now {curr:.0f}%)."
        return f"**{subject}** held steady at ~{curr:.0f}% since {period}."

    @staticmethod
    def narrative(deltas: list[ProgressDelta]) -> str:
        if not deltas:
            return "Not enough history yet — keep studying and we'll track your progress over time."
        improved = [d for d in deltas if d.delta >= 5]
        declined = [d for d in deltas if d.delta <= -5]
        lines = []
        if improved:
            lines.append(improved[0].insight)
        if declined:
            lines.append(declined[0].insight)
        if not lines:
            lines.append("Your scores are stable — consistent study will unlock bigger gains.")
        return " ".join(lines)
