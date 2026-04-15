from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text

from app.core.config import settings
from app.infrastructure.db.db import engine
from app.infrastructure.ml.ootd_service import get_ootd_service
from app.infrastructure.queue.tryon_queue import (
    get_tryon_queue_health,
    get_tryon_worker_heartbeat,
)
from app.infrastructure.queue.redis_client import get_redis_client
from app.infrastructure.storage.s3 import s3_client


def build_backend_liveness_payload() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "backend",
    }


async def check_postgres_health() -> dict[str, Any]:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


async def check_redis_health() -> dict[str, Any]:
    try:
        redis_client = get_redis_client()
        redis_ok = bool(await redis_client.ping())
        if not redis_ok:
            return {"status": "error", "reason": "Redis ping returned false"}
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "reason": str(exc)}


def _check_minio_health_sync() -> dict[str, Any]:
    client = s3_client.client
    if client is None:
        return {
            "status": "error",
            "reason": "MinIO client is unavailable",
        }

    client.head_bucket(Bucket=s3_client.bucket_name)
    return {
        "status": "ok",
        "bucket": s3_client.bucket_name,
        "endpoint": settings.S3_ENDPOINT,
    }


async def check_minio_health() -> dict[str, Any]:
    try:
        return await asyncio.to_thread(_check_minio_health_sync)
    except Exception as exc:
        return {
            "status": "error",
            "bucket": s3_client.bucket_name,
            "endpoint": settings.S3_ENDPOINT,
            "reason": str(exc),
        }


async def build_backend_readiness_payload() -> dict[str, Any]:
    postgres, redis, minio = await asyncio.gather(
        check_postgres_health(),
        check_redis_health(),
        check_minio_health(),
    )
    checks = {
        "postgres": postgres,
        "redis": redis,
        "minio": minio,
    }
    failed_checks = [name for name, payload in checks.items() if payload.get("status") == "error"]
    return {
        "status": "ok" if not failed_checks else "degraded",
        "service": "backend",
        "checks": checks,
    }


def build_tryon_service_health_payload() -> dict[str, Any]:
    ml_service = get_ootd_service()
    return ml_service.health_check()


async def build_tryon_worker_health_payload() -> dict[str, Any]:
    try:
        heartbeat = await get_tryon_worker_heartbeat()
        queue_health = await get_tryon_queue_health()
    except Exception as exc:
        return {
            "status": "degraded",
            "reason": f"Redis unavailable: {str(exc)}",
            "worker_alive": False,
            "worker": None,
            "queue": None,
        }

    if heartbeat is None:
        return {
            "status": "degraded",
            "reason": "try-on worker heartbeat is missing",
            "worker_alive": False,
            "worker": None,
            "queue": queue_health,
        }

    updated_at_raw = heartbeat.get("updated_at")
    age_seconds = None
    worker_alive = False
    if isinstance(updated_at_raw, str):
        try:
            updated_at = datetime.fromisoformat(updated_at_raw.replace("Z", "+00:00"))
            age_seconds = max(0.0, (datetime.now(timezone.utc) - updated_at).total_seconds())
            worker_alive = age_seconds <= settings.TRYON_WORKER_HEARTBEAT_TTL_SECONDS * 2
        except ValueError:
            age_seconds = None

    cuda_available = bool(heartbeat.get("cuda_available"))
    require_cuda = bool(heartbeat.get("tryon_require_cuda", settings.TRYON_REQUIRE_CUDA))
    cuda_ok = cuda_available or not require_cuda

    reason = None
    if not worker_alive:
        reason = "worker heartbeat is stale"
    elif not cuda_ok:
        reason = "worker has no CUDA but TRYON_REQUIRE_CUDA=true"

    return {
        "status": "ok" if worker_alive and cuda_ok else "degraded",
        "reason": reason,
        "worker_alive": worker_alive,
        "heartbeat_age_seconds": age_seconds,
        "worker": heartbeat,
        "queue": queue_health,
    }


async def build_tryon_queue_health_payload() -> dict[str, Any]:
    return await get_tryon_queue_health()
