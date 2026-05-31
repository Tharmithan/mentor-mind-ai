"""Unit tests — JWT tokens (Week 8 · Day 3)."""

from app.auth.jwt import (
    TOKEN_TYPE_ACCESS,
    TOKEN_TYPE_REFRESH,
    create_access_token,
    create_refresh_token,
    safe_decode,
)


def test_access_token_payload():
    token, expires_in = create_access_token("user-1", "a@b.com", "student")
    assert expires_in > 0
    payload = safe_decode(token)
    assert payload is not None
    assert payload["sub"] == "user-1"
    assert payload["email"] == "a@b.com"
    assert payload["type"] == TOKEN_TYPE_ACCESS


def test_refresh_token_payload():
    token, jti, expires_at = create_refresh_token("user-1")
    assert jti
    assert expires_at
    payload = safe_decode(token)
    assert payload is not None
    assert payload["type"] == TOKEN_TYPE_REFRESH
    assert payload["jti"] == jti


def test_invalid_token_returns_none():
    assert safe_decode("not.a.valid.jwt") is None
