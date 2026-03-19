import asyncio
import importlib
import sys


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
