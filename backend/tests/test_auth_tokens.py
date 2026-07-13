"""Tests for JWT creation/validation."""
import pytest
from fastapi import HTTPException


def test_token_roundtrip():
    from app.auth.jwt_handler import create_access_token, verify_token

    token = create_access_token({"sub": "user@example.com"})
    payload = verify_token(token, HTTPException(status_code=401))
    assert payload["sub"] == "user@example.com"


def test_tampered_token_rejected():
    from app.auth.jwt_handler import create_access_token, verify_token

    token = create_access_token({"sub": "user@example.com"})
    tampered = token[:-4] + ("aaaa" if token[-4:] != "aaaa" else "bbbb")

    exc = HTTPException(status_code=401)
    with pytest.raises(HTTPException):
        verify_token(tampered, exc)


def test_garbage_token_rejected():
    from app.auth.jwt_handler import verify_token

    with pytest.raises(HTTPException):
        verify_token("not-a-jwt", HTTPException(status_code=401))
