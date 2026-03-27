import asyncio
import importlib
import sys
import types


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


def test_run_tryon_cleanup_removes_records_storage_and_runtime_artifacts(monkeypatch):
    module = reload_tryon_cleanup_module()
    deleted_runtime_keys = []

    class FakeAsyncSessionContext:
        async def __aenter__(self):
            return object()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeTryOnRepository:
        async def get_cleanup_candidates(self, db, older_than, limit):
            assert limit == 5
            return [
                types.SimpleNamespace(id=7, avatar_media_id=10, cloth_media_id=11, result_media_id=12),
                types.SimpleNamespace(id=8, avatar_media_id=10, cloth_media_id=None, result_media_id=None),
            ]

        async def delete_many(self, db, session_ids):
            assert session_ids == [7, 8]
            return 2

    class FakeTryOnEventRepository:
        async def delete_by_session_ids(self, db, session_ids):
            assert session_ids == [7, 8]
            return 4

    class FakeMediaRepository:
        async def get_by_ids(self, db, media_ids):
            assert media_ids == [10, 11, 12]
            return [
                types.SimpleNamespace(storage_key="media/10.png"),
                types.SimpleNamespace(storage_key="media/11.png"),
                types.SimpleNamespace(storage_key="media/12.png"),
            ]

        async def delete_many(self, db, media_ids):
            assert media_ids == [10, 11, 12]
            return 3

        def delete_storage(self, storage_key):
            return {
                "local_deleted": storage_key != "media/12.png",
                "s3_deleted": storage_key == "media/12.png",
            }

    async def fake_delete_runtime_artifacts(session_id):
        deleted_runtime_keys.append(session_id)

    async def fake_trim_dead_letters(max_items):
        assert max_items == 50
        return 6

    monkeypatch.setattr(module.settings, "TRYON_RETENTION_DAYS", 30)
    monkeypatch.setattr(module.settings, "TRYON_CLEANUP_BATCH_SIZE", 5)
    monkeypatch.setattr(module.settings, "TRYON_DEAD_LETTER_MAX_ITEMS", 50)
    monkeypatch.setattr(module, "AsyncSessionLocal", lambda: FakeAsyncSessionContext())
    monkeypatch.setattr(module, "TryOnRepository", FakeTryOnRepository)
    monkeypatch.setattr(module, "TryOnEventRepository", FakeTryOnEventRepository)
    monkeypatch.setattr(module, "MediaRepository", FakeMediaRepository)
    monkeypatch.setattr(module, "delete_tryon_runtime_artifacts", fake_delete_runtime_artifacts)
    monkeypatch.setattr(module, "trim_tryon_dead_letter_queue", fake_trim_dead_letters)

    payload = asyncio.run(module.run_tryon_cleanup(force=True))

    assert payload == {
        "ran": True,
        "forced": True,
        "deleted_events": 4,
        "deleted_sessions": 2,
        "deleted_media_records": 3,
        "deleted_storage_items": 3,
        "deleted_runtime_keys": 2,
        "trimmed_dead_letters": 6,
    }
    assert deleted_runtime_keys == [7, 8]
