import asyncio
import importlib
import sys

import pytest
from fastapi import HTTPException


class FakeRedis:
    def __init__(self):
        self.storage = {}
        self.expiry = {}

    async def incr(self, key):
        next_value = int(self.storage.get(key, 0)) + 1
        self.storage[key] = next_value
        return next_value

    async def expire(self, key, seconds):
        self.expiry[key] = seconds
        return True


def reload_tryon_rate_limit_module():
    sys.modules.pop("app.core.tryon_rate_limit", None)
    return importlib.import_module("app.core.tryon_rate_limit")


def test_consume_tryon_rate_limit_allows_requests_within_window(monkeypatch):
    module = reload_tryon_rate_limit_module()
    fake_redis = FakeRedis()
    monkeypatch.setattr(module, "get_redis_client", lambda: fake_redis)
    monkeypatch.setattr(module.settings, "TRYON_RATE_LIMIT_REQUESTS", 2)
    monkeypatch.setattr(module.settings, "TRYON_RATE_LIMIT_WINDOW_SECONDS", 60)
    monkeypatch.setattr(module.time, "time", lambda: 1700000000)

    async def scenario():
        first = await module.consume_tryon_rate_limit(user_id=7)
        second = await module.consume_tryon_rate_limit(user_id=7)
        return first, second

    first, second = asyncio.run(scenario())

    assert first["allowed"] is True
    assert first["remaining"] == 1
    assert second["allowed"] is True
    assert second["remaining"] == 0
    assert fake_redis.expiry[module.build_tryon_rate_limit_key(7, 1700000000 // 60)] == 61


def test_consume_tryon_rate_limit_blocks_when_limit_exceeded(monkeypatch):
    module = reload_tryon_rate_limit_module()
    fake_redis = FakeRedis()
    monkeypatch.setattr(module, "get_redis_client", lambda: fake_redis)
    monkeypatch.setattr(module.settings, "TRYON_RATE_LIMIT_REQUESTS", 1)
    monkeypatch.setattr(module.settings, "TRYON_RATE_LIMIT_WINDOW_SECONDS", 60)
    monkeypatch.setattr(module.time, "time", lambda: 1700000030)

    async def scenario():
        await module.consume_tryon_rate_limit(user_id=9)
        return await module.consume_tryon_rate_limit(user_id=9)

    payload = asyncio.run(scenario())

    assert payload["allowed"] is False
    assert payload["retry_after"] == 10
    assert payload["remaining"] == 0


def test_enforce_tryon_rate_limit_raises_429(monkeypatch):
    module = reload_tryon_rate_limit_module()

    async def fake_consume(user_id):
        assert user_id == 12
        return {
            "allowed": False,
            "limit": 3,
            "remaining": 0,
            "retry_after": 25,
            "count": 4,
            "window_seconds": 60,
        }

    monkeypatch.setattr(module, "consume_tryon_rate_limit", fake_consume)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(module.enforce_tryon_rate_limit(12))

    assert exc_info.value.status_code == 429
    assert exc_info.value.headers["Retry-After"] == "25"
    assert exc_info.value.detail["limit"] == 3
