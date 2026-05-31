"""Integration tests — interview coach (Week 8 · Day 3)."""

from __future__ import annotations


def test_interview_types(client):
    resp = client.get("/api/interview/types")
    assert resp.status_code == 200
    types = resp.json()
    assert len(types) >= 3
    ids = {t["id"] for t in types}
    assert "technical" in ids or "hr" in ids


def test_interview_session_flow(client):
    start = client.post(
        "/api/interview/start",
        json={"interview_type": "behavioral", "num_questions": 2},
    )
    assert start.status_code == 200
    data = start.json()
    session_id = data["session_id"]
    assert data["current_question"]["text"]

    answer = client.post(
        f"/api/interview/session/{session_id}/answer",
        json={
            "answer_text": (
                "I led a team project where we improved study habits by setting "
                "weekly goals and tracking progress. We used retrospectives to "
                "learn from mistakes and celebrated small wins to stay motivated."
            ),
        },
    )
    assert answer.status_code == 200
    turn = answer.json()
    assert turn["turn"]["overall_score"] >= 0
    assert turn["turn"]["feedback_summary"]

    session = client.get(f"/api/interview/session/{session_id}")
    assert session.status_code == 200
    assert len(session.json()["turns"]) >= 1
