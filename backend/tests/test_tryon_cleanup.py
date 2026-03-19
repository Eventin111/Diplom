import asyncio
import importlib
import sys


class FakeRedis:
    def __init__(self, dead_letter_items=None):
        self.storage = {}
        self.dead_letter_items = list(dead_letter_items or [])
        self.deleted_keys = []

    async def delete(self, *keys):
        self.deleted_keys.extend(keys)
        for key in keys:
            self.storage.pop(key, None)

    async def llen(self, key):
        return len(self.dead_letter_items)

    async def ltrim(self, key, start, end):
        if end < start:
            self.dead_letter_items = []
            return True
        self.dead_letter_items = self.dead_letter_items[start : end + 1]
        return True


def reload_tryon_queue_module():
    sys.modules.pop("app.core.tryon_queue", None)
    return importlib.import_module("app.core.tryon_queue")


def reload_tryon_cleanup_module():
    sys.modules.pop("app.core.tryon_cleanup", None)
    return importlib.import_module("app.core.tryon_cleanup")


def test_trim_tryon_dead_letter_queue_removes_old_tail(monkeypatch):
    module = reload_tryon_queue_module()
    fake_redis = FakeRedis(dead_letter_items=["a", "b", "c", "d"])
    monkeypatch.setattr(module, "get_redis_client", lambda: fake_redis)

    removed = asyncio.run(module.trim_tryon_dead_letter_queue(2))

    assert removed == 2
    assert fake_redis.dead_letter_items == ["a", "b"]


def test_delete_tryon_runtime_artifacts_deletes_snapshot_and_lock(monkeypatch):
    module = reload_tryon_queue_module()
    fake_redis = FakeRedis()
    monkeypatch.setattr(module, "get_redis_client", lambda: fake_redis)

    asyncio.run(module.delete_tryon_runtime_artifacts(33))

    assert "tryon:task:33" in fake_redis.deleted_keys
    assert "tryon:processing:33" in fake_redis.deleted_keys


def test_maybe_run_periodic_tryon_cleanup_skips_until_interval(monkeypatch):
    module = reload_tryon_cleanup_module()
    monkeypatch.setattr(module.settings, "TRYON_CLEANUP_INTERVAL_SECONDS", 60)
    module._last_cleanup_run_at = 100.0
    monkeypatch.setattr(module.time, "time", lambda: 120.0)

    async def forbidden_run(force=False):
        raise AssertionError("cleanup should not run")

    monkeypatch.setattr(module, "run_tryon_cleanup", forbidden_run)

    payload = asyncio.run(module.maybe_run_periodic_tryon_cleanup())

    assert payload["ran"] is False
    assert payload["deleted_sessions"] == 0


def test_maybe_run_periodic_tryon_cleanup_executes_after_interval(monkeypatch):
    module = reload_tryon_cleanup_module()
    monkeypatch.setattr(module.settings, "TRYON_CLEANUP_INTERVAL_SECONDS", 60)
    module._last_cleanup_run_at = 100.0
    monkeypatch.setattr(module.time, "time", lambda: 170.0)

    async def fake_run(force=False):
        assert force is False
        return {"ran": True, "deleted_sessions": 4}

    monkeypatch.setattr(module, "run_tryon_cleanup", fake_run)

    payload = asyncio.run(module.maybe_run_periodic_tryon_cleanup())

    assert payload == {"ran": True, "deleted_sessions": 4}
