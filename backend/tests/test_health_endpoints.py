import asyncio
import json
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from app.core import health as health_module
from app.presentation.api.v1 import health as health_api


def test_backend_readiness_contains_only_backend_dependencies(monkeypatch):
    async def fake_postgres_health():
        return {"status": "ok", "checked_at": "2026-01-01T00:00:00+00:00"}

    async def fake_redis_health():
        return {"status": "ok", "checked_at": "2026-01-01T00:00:00+00:00"}

    async def fake_minio_health():
        return {"status": "ok", "checked_at": "2026-01-01T00:00:00+00:00"}

    monkeypatch.setattr(health_module, "check_postgres_health", fake_postgres_health)
    monkeypatch.setattr(health_module, "check_redis_health", fake_redis_health)
    monkeypatch.setattr(health_module, "check_minio_health", fake_minio_health)

    payload = asyncio.run(health_module.build_backend_readiness_payload())

    assert payload["status"] == "ok"
    assert payload["ready"] is True
    assert payload["summary"]["failed"] == 0
    assert payload["checks"]["postgres"]["status"] == "ok"
    assert payload["checks"]["redis"]["status"] == "ok"
    assert payload["checks"]["minio"]["status"] == "ok"


def test_backend_readiness_returns_503_for_failed_dependency(monkeypatch):
    async def fake_readiness_payload():
        return {
            "status": "degraded",
            "service": "backend",
            "ready": False,
            "summary": {"failed": 1, "failed_checks": ["postgres"]},
            "checks": {
                "postgres": {"status": "error", "reason": "postgres down"},
                "redis": {"status": "ok"},
                "minio": {"status": "ok"},
            },
        }

    monkeypatch.setattr(health_api, "build_backend_readiness_payload", fake_readiness_payload)

    response = asyncio.run(health_api.backend_readiness())

    assert response.status_code == 503
    assert json.loads(response.body)["checks"]["postgres"]["status"] == "error"


def test_backend_liveness_returns_ok():
    response = asyncio.run(health_api.backend_liveness())

    assert response["status"] == "ok"
    assert response["service"] == "backend"
    assert "checked_at" in response


def test_check_minio_health_returns_error_when_client_is_unavailable(monkeypatch):
    class UnavailableClient:
        @property
        def client(self):
            return None

        bucket_name = "swipeit-media"

    monkeypatch.setattr(health_module, "s3_client", UnavailableClient())

    payload = asyncio.run(health_module.check_minio_health())

    assert payload["status"] == "error"
    assert payload["reason"] == "MinIO client is unavailable"
    assert payload["critical"] is True


def test_check_postgres_health_returns_ok(monkeypatch):
    class FakeConnection:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def execute(self, _query):
            return None

    monkeypatch.setattr(health_module, "engine", SimpleNamespace(connect=lambda: FakeConnection()))

    payload = asyncio.run(health_module.check_postgres_health())

    assert payload["status"] == "ok"
    assert payload["critical"] is True
    assert "checked_at" in payload
    assert "latency_ms" in payload


def test_check_redis_health_returns_error_when_ping_is_false(monkeypatch):
    class FakeRedisClient:
        async def ping(self):
            return False

    monkeypatch.setattr(health_module, "get_redis_client", lambda: FakeRedisClient())

    payload = asyncio.run(health_module.check_redis_health())

    assert payload["status"] == "error"
    assert payload["reason"] == "Redis ping returned false"
    assert payload["critical"] is True


def test_tryon_worker_health_returns_ok_for_fresh_heartbeat(monkeypatch):
    now = datetime.now(timezone.utc)

    async def fake_get_heartbeat():
        return {
            "updated_at": now.isoformat(),
            "cuda_available": True,
            "tryon_require_cuda": True,
        }

    async def fake_get_queue_health():
        return {"status": "ok"}

    monkeypatch.setattr(health_module, "get_tryon_worker_heartbeat", fake_get_heartbeat)
    monkeypatch.setattr(health_module, "get_tryon_queue_health", fake_get_queue_health)

    payload = asyncio.run(health_module.build_tryon_worker_health_payload())

    assert payload["status"] == "ok"
    assert payload["worker_alive"] is True
    assert payload["reason"] is None
    assert payload["queue"] == {"status": "ok"}
    assert payload["component"] == "worker"


def test_tryon_worker_health_returns_degraded_for_missing_heartbeat(monkeypatch):
    async def fake_get_heartbeat():
        return None

    async def fake_get_queue_health():
        return {"status": "ok"}

    monkeypatch.setattr(health_module, "get_tryon_worker_heartbeat", fake_get_heartbeat)
    monkeypatch.setattr(health_module, "get_tryon_queue_health", fake_get_queue_health)

    payload = asyncio.run(health_module.build_tryon_worker_health_payload())

    assert payload["status"] == "disabled"
    assert payload["reason"] == "try-on worker heartbeat is missing"
    assert payload["queue"] == {"status": "ok"}


def test_tryon_worker_health_returns_degraded_for_stale_heartbeat(monkeypatch):
    stale_time = datetime.now(timezone.utc) - timedelta(
        seconds=health_module.settings.TRYON_WORKER_HEARTBEAT_TTL_SECONDS * 3
    )

    async def fake_get_heartbeat():
        return {
            "updated_at": stale_time.isoformat(),
            "cuda_available": True,
            "tryon_require_cuda": False,
        }

    async def fake_get_queue_health():
        return {"status": "ok"}

    monkeypatch.setattr(health_module, "get_tryon_worker_heartbeat", fake_get_heartbeat)
    monkeypatch.setattr(health_module, "get_tryon_queue_health", fake_get_queue_health)

    payload = asyncio.run(health_module.build_tryon_worker_health_payload())

    assert payload["status"] == "degraded"
    assert payload["worker_alive"] is False
    assert payload["reason"] == "worker heartbeat is stale"


def test_tryon_model_health_returns_disabled_when_ml_dependency_is_missing(monkeypatch):
    original_import = __import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "app.infrastructure.ml.ootd_service":
            raise ModuleNotFoundError("No module named 'cv2'", name="cv2")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", fake_import)

    payload = health_module.check_tryon_model_health()

    assert payload["status"] == "disabled"
    assert payload["enabled"] is False
    assert payload["reason"] == "Optional ML dependency is unavailable: cv2"


def test_tryon_service_health_returns_503_when_feature_is_disabled(monkeypatch):
    def fake_model_health():
        return {"status": "disabled", "reason": "try-on runtime is disabled"}

    async def fake_worker_health():
        return {"status": "disabled", "reason": "worker is disabled"}

    async def fake_queue_health():
        return {"status": "ok", "reason": None}

    monkeypatch.setattr(health_module, "check_tryon_model_health", fake_model_health)
    monkeypatch.setattr(
        health_api,
        "build_tryon_service_health_payload",
        health_module.build_tryon_service_health_payload,
    )
    monkeypatch.setattr(health_module, "build_tryon_worker_health_payload", fake_worker_health)
    monkeypatch.setattr(health_module, "build_tryon_queue_health_payload", fake_queue_health)

    response = asyncio.run(health_api.tryon_health())
    body = json.loads(response.body)

    assert response.status_code == 503
    assert body["status"] == "disabled"
    assert body["ready"] is False


def test_tryon_queue_health_returns_503_for_failed_queue(monkeypatch):
    async def fake_queue_payload():
        return {
            "status": "error",
            "reason": "Redis unavailable",
        }

    monkeypatch.setattr(health_api, "build_tryon_queue_health_payload", fake_queue_payload)

    response = asyncio.run(health_api.tryon_queue_health())

    assert response.status_code == 503
    assert json.loads(response.body)["status"] == "error"


def test_tryon_worker_health_returns_503_for_degraded_worker(monkeypatch):
    async def fake_worker_payload():
        return {
            "status": "degraded",
            "reason": "worker heartbeat is stale",
        }

    monkeypatch.setattr(health_api, "build_tryon_worker_health_payload", fake_worker_payload)

    response = asyncio.run(health_api.tryon_worker_health())

    assert response.status_code == 503
    assert json.loads(response.body)["status"] == "degraded"
