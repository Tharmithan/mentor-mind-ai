"""Integration tests — AI module: prediction & recommendations (Week 8 · Day 3)."""

from __future__ import annotations


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "mentormind-api"


def test_predict_performance(client):
    resp = client.post(
        "/api/predict",
        json={"study_hours": 5, "attendance": 82, "sleep_hours": 7},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "prediction" in data
    assert "confidence" in data
    assert 0 <= data["predicted_score"] <= 100
    assert data["student_risk"] is not None


def test_predict_validation_rejects_invalid(client):
    resp = client.post(
        "/api/predict",
        json={"study_hours": -1, "attendance": 82, "sleep_hours": 7},
    )
    assert resp.status_code == 422


def test_recommendations(client):
    resp = client.get("/api/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)


def test_ai_status(client):
    resp = client.get("/api/ai/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "models_loaded" in data
    assert "modules" in data
