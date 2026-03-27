import asyncio
import importlib
import sys

import pytest
from fastapi import HTTPException


def load_security_module():
    sys.modules.pop("app.core.security", None)
    sys.modules.pop("app.infrastructure.auth.security", None)
    importlib.import_module("app.core.security")
    return importlib.import_module("app.infrastructure.auth.security")


def test_hash_password_and_verify_password():
    from app.core.hashing import hash_password, verify_password

    hashed = hash_password("secret123")

    assert hashed != "secret123"
    assert verify_password("secret123", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_verify_password_returns_false_for_unknown_hash():
    from app.core.hashing import verify_password

    assert verify_password("secret123", "not-a-passlib-hash") is False


def test_create_token_contains_subject_and_exp():
    security = load_security_module()
    token = security.create_token(sub=15, ttl_min=5)
    payload = security.jwt.decode(token, security.settings.SECRET_KEY, algorithms=["HS256"])

    assert payload["sub"] == "15"
    assert payload["exp"] > payload["iat"]


def test_get_current_user_returns_repository_result(monkeypatch):
    security = load_security_module()

    class DummyRepo:
        async def get(self, db, user_id):
            assert db == "db-session"
            assert user_id == 25
            return {"id": user_id}

    monkeypatch.setattr(security, "UserRepository", DummyRepo)

    token = security.create_token(sub=25, ttl_min=5)
    user = asyncio.run(security.get_current_user(token=token, db="db-session"))

    assert user == {"id": 25}


def test_get_current_user_raises_for_invalid_token():
    security = load_security_module()

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(security.get_current_user(token="bad-token", db="db"))

    assert exc_info.value.status_code == 401


def test_get_current_user_raises_when_user_missing(monkeypatch):
    security = load_security_module()

    class DummyRepo:
        async def get(self, db, user_id):
            return None

    monkeypatch.setattr(security, "UserRepository", DummyRepo)

    token = security.create_token(sub=5, ttl_min=5)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(security.get_current_user(token=token, db="db"))

    assert exc_info.value.status_code == 401
