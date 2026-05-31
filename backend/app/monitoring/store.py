"""Feedback & monitoring JSON store (Week 7 · Day 6)."""

from __future__ import annotations

import json
from pathlib import Path

MONITORING_DIR = Path(__file__).resolve().parents[2] / "uploads" / "monitoring"
FEEDBACK_JSON = MONITORING_DIR / "feedback.json"
PREDICTION_LOGS_JSON = MONITORING_DIR / "prediction_logs.json"


class MonitoringStore:
    def __init__(self) -> None:
        MONITORING_DIR.mkdir(parents=True, exist_ok=True)

    def load_feedback(self) -> list[dict]:
        if FEEDBACK_JSON.exists():
            return json.loads(FEEDBACK_JSON.read_text(encoding="utf-8"))
        return []

    def save_feedback(self, entries: list[dict]) -> None:
        FEEDBACK_JSON.write_text(json.dumps(entries, indent=2), encoding="utf-8")

    def load_predictions(self) -> list[dict]:
        if PREDICTION_LOGS_JSON.exists():
            return json.loads(PREDICTION_LOGS_JSON.read_text(encoding="utf-8"))
        return []

    def save_predictions(self, entries: list[dict]) -> None:
        PREDICTION_LOGS_JSON.write_text(json.dumps(entries, indent=2), encoding="utf-8")


_store: MonitoringStore | None = None


def get_monitoring_store() -> MonitoringStore:
    global _store
    if _store is None:
        _store = MonitoringStore()
    return _store
