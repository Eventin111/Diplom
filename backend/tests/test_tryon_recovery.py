import asyncio
import importlib
import sys
import types


def reload_tryon_recovery_module():
    sys.modules.pop("app.core.tryon_recovery", None)
    return importlib.import_module("app.core.tryon_recovery")


def test_maybe_run_periodic_tryon_recovery_skips_until_interval(monkeypatch):
    module = reload_tryon_recovery_module()
    monkeypatch.setattr(module.settings, "TRYON_RECOVERY_INTERVAL_SECONDS", 60)
    module._last_recovery_run_at = 100.0
    monkeypatch.setattr(module.time, "time", lambda: 120.0)

    async def forbidden_run(force=False):
        raise AssertionError("recovery should not run")

    monkeypatch.setattr(module, "run_tryon_recovery", forbidden_run)

    payload = asyncio.run(module.maybe_run_periodic_tryon_recovery())

    assert payload["ran"] is False
    assert payload["recovered_session_ids"] == []


def test_maybe_run_periodic_tryon_recovery_executes_after_interval(monkeypatch):
    module = reload_tryon_recovery_module()
    monkeypatch.setattr(module.settings, "TRYON_RECOVERY_INTERVAL_SECONDS", 60)
    module._last_recovery_run_at = 100.0
    monkeypatch.setattr(module.time, "time", lambda: 170.0)

    async def fake_run(force=False):
        assert force is False
        return {"ran": True, "recovered_session_ids": [5], "skipped": []}

    monkeypatch.setattr(module, "run_tryon_recovery", fake_run)

    payload = asyncio.run(module.maybe_run_periodic_tryon_recovery())

    assert payload == {"ran": True, "recovered_session_ids": [5], "skipped": []}


def test_run_tryon_recovery_requeues_stale_sessions_without_locks(monkeypatch):
    module = reload_tryon_recovery_module()
    updated_statuses = []
    enqueued_tasks = []
    created_events = []

    class FakeAsyncSessionContext:
        async def __aenter__(self):
            return object()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    class FakeTryOnRepository:
        async def get_stale_processing_sessions(self, db, older_than):
            return [
                types.SimpleNamespace(id=1),
                types.SimpleNamespace(id=2),
                types.SimpleNamespace(id=3),
            ]

        async def update_status(self, db, session_id, status, error_text=None):
            updated_statuses.append((session_id, status, error_text))

    class FakeTryOnEventRepository:
        async def create_event(self, db, session_id, event_type, attempt, details):
            created_events.append((session_id, event_type, attempt, details))

    async def fake_has_lock(session_id):
        return session_id == 1

    async def fake_get_snapshot(session_id):
        if session_id == 2:
            return None
        return {"session_id": session_id, "attempt": 5}

    async def fake_enqueue_tryon_task(task):
        enqueued_tasks.append(task)

    monkeypatch.setattr(module.settings, "TRYON_STALE_PROCESSING_THRESHOLD_SECONDS", 300)
    monkeypatch.setattr(module, "AsyncSessionLocal", lambda: FakeAsyncSessionContext())
    monkeypatch.setattr(module, "TryOnRepository", FakeTryOnRepository)
    monkeypatch.setattr(module, "TryOnEventRepository", FakeTryOnEventRepository)
    monkeypatch.setattr(module, "has_tryon_processing_lock", fake_has_lock)
    monkeypatch.setattr(module, "get_tryon_task_snapshot", fake_get_snapshot)
    monkeypatch.setattr(module, "enqueue_tryon_task", fake_enqueue_tryon_task)

    payload = asyncio.run(module.run_tryon_recovery(force=True))

    assert payload == {
        "ran": True,
        "forced": True,
        "recovered_session_ids": [3],
        "skipped": [
            {"session_id": 1, "reason": "processing lock is still active"},
            {"session_id": 2, "reason": "task snapshot not found"},
        ],
        "stale_threshold_seconds": 300,
    }
    assert updated_statuses == [(3, module.TryOnStatus.QUEUED, None)]
    assert enqueued_tasks == [{"session_id": 3, "attempt": 0}]
    assert created_events == [
        (3, module.TryOnEventType.RECOVERED, 0, "Recovered stale processing session")
    ]
