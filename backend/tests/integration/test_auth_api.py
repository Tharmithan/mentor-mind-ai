"""Integration tests — auth API: signup, login, logout (Week 8 · Day 3)."""

from __future__ import annotations


def test_register_login_me_logout(client, unique_email):
    password = "SecurePass1"

    # Signup
    reg = client.post(
        "/api/auth/register",
        json={"email": unique_email, "password": password, "full_name": "Test Student"},
    )
    assert reg.status_code == 200
    body = reg.json()
    assert body["token_type"] == "bearer"
    assert body["user"]["email"] == unique_email
    access = body["access_token"]
    refresh = body["refresh_token"]

    # Me
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200
    assert me.json()["email"] == unique_email

    # Login
    login = client.post(
        "/api/auth/login",
        json={"email": unique_email, "password": password},
    )
    assert login.status_code == 200
    assert login.json()["access_token"]

    # Refresh
    refreshed = client.post("/api/auth/refresh", json={"refresh_token": refresh})
    assert refreshed.status_code == 200
    new_refresh = refreshed.json()["refresh_token"]

    # Logout
    logout = client.post("/api/auth/logout", json={"refresh_token": new_refresh})
    assert logout.status_code == 200
    assert logout.json()["message"] == "Logged out"


def test_login_invalid_password(client, unique_email):
    client.post(
        "/api/auth/register",
        json={"email": unique_email, "password": "SecurePass1", "full_name": "X"},
    )
    bad = client.post(
        "/api/auth/login",
        json={"email": unique_email, "password": "WrongPass1"},
    )
    assert bad.status_code == 401


def test_register_weak_password_rejected(client, unique_email):
    weak = client.post(
        "/api/auth/register",
        json={"email": unique_email, "password": "weak", "full_name": "X"},
    )
    assert weak.status_code == 422


def test_me_requires_auth(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
