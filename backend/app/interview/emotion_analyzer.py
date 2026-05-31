"""Emotion & confidence aggregation (Week 5 · Day 5).

Client sends webcam/voice metrics; server aggregates and adds delivery tips.
Optional OpenCV path for future server-side FER on uploaded frames.
"""

from __future__ import annotations


def aggregate_emotion_metrics(samples: list[dict]) -> dict:
    """Average client snapshots into one payload."""
    if not samples:
        return {}
    keys = [
        "confidence",
        "stress",
        "nervousness",
        "engagement",
        "eye_contact",
        "smile",
        "attention",
    ]
    out: dict = {"samples": len(samples)}
    for k in keys:
        vals = [s[k] for s in samples if k in s and isinstance(s[k], (int, float))]
        if vals:
            out[k] = round(sum(vals) / len(vals), 1)
    emotions = [s.get("dominant_emotion") for s in samples if s.get("dominant_emotion")]
    if emotions:
        out["dominant_emotion"] = max(set(emotions), key=emotions.count)
    return out


def delivery_tips(metrics: dict) -> list[str]:
    """Human tips from averaged emotion metrics."""
    tips: list[str] = []
    if metrics.get("eye_contact", 70) < 55:
        tips.append("Try improving eye contact — look at the camera lens, not the screen.")
    if metrics.get("smile", 0) < 35:
        tips.append("A brief natural smile at the start/end helps you appear confident and warm.")
    if metrics.get("stress", 30) > 60 or metrics.get("nervousness", 30) > 60:
        tips.append("You showed signs of stress — pause, breathe, and reduce filler words.")
    if metrics.get("engagement", 50) < 50:
        tips.append("Stay engaged: lean slightly forward and nod when the interviewer speaks.")
    if metrics.get("attention", 70) < 55:
        tips.append("Keep your face centered in frame for better attention tracking.")
    if not tips:
        tips.append("Strong delivery — maintain steady pace and clear eye contact.")
    return tips[:4]
