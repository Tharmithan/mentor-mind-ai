"""End-to-end flows across modules (Week 8 · Day 3)."""

from __future__ import annotations


def test_e2e_auth_to_protected_mlops(client, unique_email):
    """Register → login → call protected MLOps endpoint."""
    reg = client.post(
        "/api/auth/register",
        json={"email": unique_email, "password": "SecurePass1", "full_name": "E2E User"},
    )
    assert reg.status_code == 200
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    status = client.get("/api/mlops/status", headers=headers)
    assert status.status_code == 200

    models = client.get("/api/mlops/models", headers=headers)
    assert models.status_code == 200


def test_e2e_ml_predict_and_monitor(client):
    """Predict → submit feedback loop."""
    pred = client.post(
        "/api/predict",
        json={"study_hours": 6, "attendance": 90, "sleep_hours": 8},
    )
    assert pred.status_code == 200
    body = pred.json()

    feedback = client.post(
        "/api/monitoring/feedback",
        json={
            "category": "prediction",
            "target_id": body.get("model_version", "ml"),
            "rating": 5,
            "helpful": True,
            "metadata": {"predicted_score": body["predicted_score"]},
        },
    )
    assert feedback.status_code == 200

    dash = client.get("/api/monitoring/demo")
    assert dash.status_code == 200
    assert dash.json()["model_metrics"]["total_predictions"] >= 1


def test_e2e_interview_and_coach_report(client):
    """Start interview → answer all questions → session completes."""
    start = client.post(
        "/api/interview/start",
        json={"interview_type": "hr", "num_questions": 1},
    )
    assert start.status_code == 200
    sid = start.json()["session_id"]

    ans = client.post(
        f"/api/interview/session/{sid}/answer",
        json={
            "answer_text": (
                "My greatest strength is communication. I explain complex ideas clearly "
                "to teammates and stakeholders, which helped me succeed in group projects."
            )
        },
    )
    assert ans.status_code == 200
    if ans.json().get("completed"):
        coach = client.get(f"/api/interview/session/{sid}/coach")
        assert coach.status_code in (200, 400)


def test_e2e_rag_study_flow(client):
    """Upload notes → search → chat."""
    up = client.post(
        "/api/documents/upload",
        files={"file": ("e2e.txt", b"Python lists are mutable sequences.", "text/plain")},
    )
    assert up.status_code == 200
    doc_id = up.json()["document"]["document_id"]

    chat = client.post(
        "/api/documents/chat",
        json={"question": "Explain Python lists", "document_id": doc_id},
    )
    assert chat.status_code == 200

    delete = client.delete(f"/api/documents/{doc_id}")
    assert delete.status_code == 200
