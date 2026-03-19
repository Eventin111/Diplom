import asyncio
import importlib
import json
import sys


class FakeRedis:
    def __init__(self):
        self.storage = {}

    async def get(self, key):
        return self.storage.get(key)

    async def setex(self, key, ttl, value):
        self.storage[key] = value


def reload_tryon_cache_module():
    sys.modules.pop("app.core.tryon_cache", None)
    return importlib.import_module("app.core.tryon_cache")


def test_build_tryon_cache_key_is_stable_for_identical_requests():
    module = reload_tryon_cache_module()

    key_one = module.build_tryon_cache_key(
        model_bytes=b"model",
        cloth_bytes=b"cloth",
        model_type="hd",
        category=0,
        scale=2.0,
        num_steps=4,
        num_samples=1,
        seed=42,
    )
    key_two = module.build_tryon_cache_key(
        model_bytes=b"model",
        cloth_bytes=b"cloth",
        model_type="hd",
        category=0,
        scale=2.0,
        num_steps=4,
        num_samples=1,
        seed=42,
    )

    assert key_one == key_two
    assert key_one.startswith("tryon:result:")


def test_build_tryon_cache_key_changes_when_inputs_change():
    module = reload_tryon_cache_module()

    first = module.build_tryon_cache_key(
        model_bytes=b"model-a",
        cloth_bytes=b"cloth",
        model_type="hd",
        category=0,
        scale=2.0,
        num_steps=4,
        num_samples=1,
        seed=42,
    )
    second = module.build_tryon_cache_key(
        model_bytes=b"model-b",
        cloth_bytes=b"cloth",
        model_type="hd",
        category=0,
        scale=2.0,
        num_steps=4,
        num_samples=1,
        seed=42,
    )

    assert first != second


def test_cache_tryon_result_roundtrip(monkeypatch):
    module = reload_tryon_cache_module()
    fake_redis = FakeRedis()
    monkeypatch.setattr(module, "get_redis_client", lambda: fake_redis)

    async def scenario():
        await module.cache_tryon_result(
            "tryon:result:test",
            results=["https://cdn.example.com/result.png"],
            result_media_id=123,
            ttl_seconds=60,
        )
        return await module.get_cached_tryon_result("tryon:result:test")

    payload = asyncio.run(scenario())

    assert payload == {
        "results": ["https://cdn.example.com/result.png"],
        "result_media_id": 123,
    }
    assert json.loads(fake_redis.storage["tryon:result:test"]) == payload
