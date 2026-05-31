"""Integration tests — admin dashboard (Week 8 · Bonus)."""

from __future__ import annotations


def test_admin_overview_demo(client):
    resp = client.get("/api/admin/overview/demo")
    assert resp.status_code == 200
    body = resp.json()
    assert "total_users" in body
    assert "total_predictions" in body
    assert "system_status" in body
    assert body["models_loaded"] is True or body["models_loaded"] is False
