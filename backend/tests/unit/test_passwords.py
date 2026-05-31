"""Unit tests — password hashing (Week 8 · Day 3)."""

from app.auth.passwords import hash_password, verify_password


def test_hash_and_verify_password():
    hashed = hash_password("SecurePass1")
    assert hashed != "SecurePass1"
    assert verify_password("SecurePass1", hashed)
    assert not verify_password("WrongPass1", hashed)


def test_rejects_legacy_plaintext_marker():
    assert not verify_password("Demo123!", "hashed_demo_password")
