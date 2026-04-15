import asyncio
import json

from app.core import health as health_module
from app.presentation.api.v1 import health as health_api


def test_backend_readiness_contains_only_backend_dependencies(monkeypatch):
    async def fake_postgres_health():
        return {"status": "ok"}

    async def fake_redis_health():
        return {"status": "ok"}

    async def fake_minio_health():
        return {"status": "ok"}

    monkeypatch.setattr(health_module, "check_postgres_health", fake_postgres_health)
    monkeypatch.setattr(health_module, "check_redis_health", fake_redis_health)
    monkeypatch.setattr(health_module, "check_minio_health", fake_minio_health)

    payload = asyncio.run(health_module.build_backend_readiness_payload())

    assert payload["status"] == "ok"
    assert payload["checks"] == {
        "postgres": {"status": "ok"},
        "redis": {"status": "ok"},
        "minio": {"status": "ok"},
    }


def test_backend_readiness_returns_503_for_failed_dependency(monkeypatch):
    async def fake_readiness_payload():
        return {
            "status": "degraded",
            "service": "backend",
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

    assert response == {"status": "ok", "service": "backend"}


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
