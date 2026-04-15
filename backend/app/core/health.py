from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import text

from app.core.config import project_config, settings
from app.infrastructure.db.db import engine
from app.infrastructure.queue.redis_client import get_redis_client
from app.infrastructure.queue.tryon_queue import get_tryon_queue_health, get_tryon_worker_heartbeat
from app.infrastructure.storage.s3 import s3_client


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _duration_ms(start_time: float) -> int:
    return int((time.perf_counter() - start_time) * 1000)


def _build_target(host: str | None, port: int | None) -> str | None:
    if host is None:
        return None
    return f"{host}:{port}" if port is not None else host


def _build_redis_target() -> str:
    parsed = urlparse(settings.REDIS_URL)
    return parsed.netloc or settings.REDIS_URL


def _get_tryon_runtime_device() -> str:
    return str(getattr(project_config.ml, "device", "cpu")).strip().lower() or "cpu"


def _is_tryon_interactive_supported(*, runtime_device: str, cuda_available: bool) -> bool:
    return runtime_device != "cpu" and cuda_available


def _build_tryon_interactive_reason(*, runtime_device: str, cuda_available: bool) -> str | None:
    if runtime_device == "cpu":
        return "CPU mode does not support interactive try-on within expected time"
    if not cuda_available:
        return "GPU acceleration is unavailable for interactive try-on"
    return None


def _first_non_ok_reason(*payloads: dict[str, Any]) -> str | None:
    for payload in payloads:
        if payload.get("status") != "ok" and payload.get("reason"):
            return str(payload["reason"])
    return None


def build_backend_liveness_payload() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "backend",
        "checked_at": _utc_now_iso(),
    }


async def check_postgres_health() -> dict[str, Any]:
    start_time = time.perf_counter()
    target = _build_target(settings.DB_URL.host, settings.DB_URL.port)
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "checked_at": _utc_now_iso(),
            "latency_ms": _duration_ms(start_time),
            "target": target,
            "critical": True,
        }
    except Exception as exc:
        return {
            "status": "error",
            "checked_at": _utc_now_iso(),
            "latency_ms": _duration_ms(start_time),
            "target": target,
            "critical": True,
            "reason": str(exc),
        }


async def check_redis_health() -> dict[str, Any]:
    start_time = time.perf_counter()
    target = _build_redis_target()
    try:
        redis_client = get_redis_client()
        redis_ok = bool(await redis_client.ping())
        if not redis_ok:
            return {
                "status": "error",
                "checked_at": _utc_now_iso(),
                "latency_ms": _duration_ms(start_time),
                "target": target,
                "critical": True,
                "reason": "Redis ping returned false",
            }
        return {
            "status": "ok",
            "checked_at": _utc_now_iso(),
            "latency_ms": _duration_ms(start_time),
            "target": target,
            "critical": True,
        }
    except Exception as exc:
        return {
            "status": "error",
            "checked_at": _utc_now_iso(),
            "latency_ms": _duration_ms(start_time),
            "target": target,
            "critical": True,
            "reason": str(exc),
        }


def _check_minio_health_sync() -> dict[str, Any]:
    start_time = time.perf_counter()
    client = s3_client.client
    if client is None:
        return {
            "status": "error",
            "checked_at": _utc_now_iso(),
            "latency_ms": _duration_ms(start_time),
            "target": settings.S3_ENDPOINT,
            "critical": True,
            "reason": "MinIO client is unavailable",
        }

    client.head_bucket(Bucket=s3_client.bucket_name)
    return {
        "status": "ok",
        "checked_at": _utc_now_iso(),
        "latency_ms": _duration_ms(start_time),
        "critical": True,
        "bucket": s3_client.bucket_name,
        "target": settings.S3_ENDPOINT,
    }


async def check_minio_health() -> dict[str, Any]:
    try:
        return await asyncio.to_thread(_check_minio_health_sync)
    except Exception as exc:
        return {
            "status": "error",
            "checked_at": _utc_now_iso(),
            "latency_ms": None,
            "critical": True,
            "bucket": s3_client.bucket_name,
            "target": settings.S3_ENDPOINT,
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
    checked_at = _utc_now_iso()
    return {
        "status": "ok" if not failed_checks else "degraded",
        "service": "backend",
        "ready": not failed_checks,
        "checked_at": checked_at,
        "summary": {
            "total": len(checks),
            "ok": sum(1 for payload in checks.values() if payload.get("status") == "ok"),
            "failed": len(failed_checks),
            "failed_checks": failed_checks,
        },
        "checks": checks,
    }


def check_tryon_model_health() -> dict[str, Any]:
    start_time = time.perf_counter()
    runtime_device = _get_tryon_runtime_device()
    try:
        from app.infrastructure.ml.ootd_service import get_ootd_service
    except ModuleNotFoundError as exc:
        return {
            "status": "disabled",
            "checked_at": _utc_now_iso(),
            "latency_ms": _duration_ms(start_time),
            "component": "model",
            "target": "OOTDiffusion",
            "enabled": False,
            "runtime_device": runtime_device,
            "interactive_supported": False,
            "reason": f"Optional ML dependency is unavailable: {exc.name}",
        }
    except Exception as exc:
        return {
            "status": "error",
            "checked_at": _utc_now_iso(),
            "latency_ms": _duration_ms(start_time),
            "component": "model",
            "target": "OOTDiffusion",
            "enabled": False,
            "runtime_device": runtime_device,
            "interactive_supported": False,
            "reason": str(exc),
        }

    ml_service = get_ootd_service()
    raw_payload = ml_service.health_check()
    cuda_available = bool(raw_payload.get("cuda_available"))
    interactive_supported = _is_tryon_interactive_supported(
        runtime_device=runtime_device,
        cuda_available=cuda_available,
    )
    reason = _build_tryon_interactive_reason(
        runtime_device=runtime_device,
        cuda_available=cuda_available,
    )

    return {
        "status": "ok",
        "checked_at": _utc_now_iso(),
        "latency_ms": _duration_ms(start_time),
        "component": "model",
        "target": raw_payload.get("model", "OOTDiffusion"),
        "enabled": True,
        "runtime_device": runtime_device,
        "interactive_supported": interactive_supported,
        "reason": reason,
        "details": {
            **raw_payload,
            "runtime_device": runtime_device,
        },
    }


async def build_tryon_worker_health_payload() -> dict[str, Any]:
    start_time = time.perf_counter()
    runtime_device = _get_tryon_runtime_device()
    try:
        heartbeat = await get_tryon_worker_heartbeat()
        await get_tryon_queue_health()
    except Exception as exc:
        return {
            "status": "error",
            "checked_at": _utc_now_iso(),
            "latency_ms": _duration_ms(start_time),
            "component": "worker",
            "target": settings.TRYON_WORKER_HEARTBEAT_KEY,
            "runtime_device": runtime_device,
            "interactive_supported": False,
            "reason": f"Redis unavailable: {str(exc)}",
            "worker_alive": False,
            "worker": None,
        }

    if heartbeat is None:
        return {
            "status": "disabled",
            "checked_at": _utc_now_iso(),
            "latency_ms": _duration_ms(start_time),
            "component": "worker",
            "target": settings.TRYON_WORKER_HEARTBEAT_KEY,
            "runtime_device": runtime_device,
            "interactive_supported": False,
            "reason": "try-on worker heartbeat is missing",
            "worker_alive": False,
            "worker": None,
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
    interactive_supported = _is_tryon_interactive_supported(
        runtime_device=runtime_device,
        cuda_available=cuda_available,
    )
    reason = "worker heartbeat is stale" if not worker_alive else None

    return {
        "status": "ok" if worker_alive else "degraded",
        "checked_at": _utc_now_iso(),
        "latency_ms": _duration_ms(start_time),
        "component": "worker",
        "target": settings.TRYON_WORKER_HEARTBEAT_KEY,
        "runtime_device": runtime_device,
        "interactive_supported": interactive_supported,
        "reason": reason,
        "worker_alive": worker_alive,
        "heartbeat_age_seconds": age_seconds,
        "worker": heartbeat,
    }


async def build_tryon_queue_health_payload() -> dict[str, Any]:
    start_time = time.perf_counter()
    try:
        queue_health = await get_tryon_queue_health()
    except Exception as exc:
        return {
            "status": "error",
            "checked_at": _utc_now_iso(),
            "latency_ms": _duration_ms(start_time),
            "component": "queue",
            "target": settings.TRYON_QUEUE_NAME,
            "reason": str(exc),
            "details": None,
        }

    return {
        "status": "ok" if queue_health.get("redis_ok") else "error",
        "checked_at": _utc_now_iso(),
        "latency_ms": _duration_ms(start_time),
        "component": "queue",
        "target": settings.TRYON_QUEUE_NAME,
        "reason": None if queue_health.get("redis_ok") else "Redis ping returned false",
        "details": queue_health,
    }


async def _collect_tryon_health_components() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    model = check_tryon_model_health()
    worker, queue = await asyncio.gather(
        build_tryon_worker_health_payload(),
        build_tryon_queue_health_payload(),
    )
    return model, worker, queue


async def build_tryon_live_payload() -> dict[str, Any]:
    model, worker, queue = await _collect_tryon_health_components()
    component_statuses = [model.get("status"), worker.get("status"), queue.get("status")]
    if any(component_status in {"error", "degraded"} for component_status in component_statuses):
        status = "degraded"
    else:
        status = "ok"

    return {
        "status": status,
        "service": "tryon-live",
        "ready": status == "ok",
        "checked_at": _utc_now_iso(),
        "runtime_device": str(
            model.get("runtime_device") or worker.get("runtime_device") or _get_tryon_runtime_device()
        ),
        "interactive_supported": bool(model.get("interactive_supported")) and bool(worker.get("interactive_supported")),
        "reason": _first_non_ok_reason(model, worker, queue),
        "model": model,
    }


async def build_tryon_ready_payload() -> dict[str, Any]:
    model, worker, queue = await _collect_tryon_health_components()

    runtime_device = str(model.get("runtime_device") or worker.get("runtime_device") or _get_tryon_runtime_device())
    interactive_supported = bool(model.get("interactive_supported")) and bool(worker.get("interactive_supported"))
    queue_ready = queue.get("status") == "ok"
    worker_ready = bool(worker.get("worker_alive"))
    model_enabled = bool(model.get("enabled"))

    if not model_enabled:
        status = "disabled"
    elif not queue_ready or not worker_ready:
        status = "degraded"
    elif not interactive_supported:
        status = "degraded"
    else:
        status = "ok"

    reason = _first_non_ok_reason(model, worker, queue)
    if reason is None and not interactive_supported:
        reason = _build_tryon_interactive_reason(
            runtime_device=runtime_device,
            cuda_available=bool(
                worker.get("worker", {}).get("cuda_available", model.get("details", {}).get("cuda_available", False))
            ),
        )

    return {
        "status": status,
        "service": "tryon",
        "ready": status == "ok",
        "checked_at": _utc_now_iso(),
        "runtime_device": runtime_device,
        "interactive_supported": interactive_supported,
        "reason": reason,
        "model": model,
    }
