from __future__ import annotations

import asyncio
import base64
import gc
import io
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from PIL import Image

from app.application.dto.tryon_dto import TryOnRequest
from app.application.use_cases.tryon_use_case import TryOnUseCase
from app.core.config import settings
from app.domain.enums.tryon import TryOnEventType, TryOnStatus
from app.infrastructure.cache.tryon_cache import (
    build_tryon_cache_key,
    cache_tryon_result,
    get_cached_tryon_result,
)
from app.infrastructure.db.db import AsyncSessionLocal
from app.infrastructure.db.db import engine
from app.infrastructure.db.schema_compat import ensure_schema_compatibility
from app.infrastructure.maintenance.tryon_cleanup import maybe_run_periodic_tryon_cleanup
from app.infrastructure.maintenance.tryon_recovery import maybe_run_periodic_tryon_recovery
from app.infrastructure.queue.tryon_queue import (
    acquire_tryon_processing_lock,
    dequeue_tryon_task,
    enqueue_tryon_dead_letter,
    enqueue_tryon_task,
    set_tryon_worker_heartbeat,
    release_tryon_processing_lock,
)
from app.infrastructure.ml.ootd_service import get_ootd_service
from app.infrastructure.storage.local_media import build_local_media_path
from app.infrastructure.storage.s3 import s3_client
from app.infrastructure.persistence.repositories.media_repo import MediaRepository
from app.infrastructure.persistence.repositories.tryon_event_repo import TryOnEventRepository
from app.infrastructure.persistence.repositories.tryon_repo import TryOnRepository
from app.application.dto.media_dto import MediaType


logger = logging.getLogger(__name__)


def _is_non_retriable_tryon_error(exc: Exception) -> bool:
    error_message = str(exc).lower()
    error_type = exc.__class__.__name__.lower()
    known_non_retriable_markers = (
        "cuda out of memory",
        "outofmemoryerror",
        "no_suchfile",
        "file doesn't exist",
        "no such file or directory",
        "failed:load model from",
    )
    return error_type.endswith("outofmemoryerror") or any(
        marker in error_message for marker in known_non_retriable_markers
    )


def _media_file_url(media_id: Optional[int]) -> Optional[str]:
    if media_id is None:
        return None
    return f"{settings.API_V1}/media/{media_id}/file"


def _release_cuda_memory() -> None:
    gc.collect()
    try:
        import torch
    except Exception:
        return
    if not torch.cuda.is_available():
        return
    try:
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
    except Exception as exc:
        logger.debug("Failed to release CUDA cache: %s", exc)


def _get_cuda_runtime_snapshot() -> dict[str, object]:
    visible_devices = str(os.getenv("NVIDIA_VISIBLE_DEVICES", "")).strip().lower()
    runtime_hint = str(os.getenv("TRYON_RUNTIME", "")).strip().lower()
    cuda_hint = visible_devices not in {"", "none", "void"} or runtime_hint == "nvidia"
    cuda_available = cuda_hint
    gpu_name = None
    gpu_memory_total_mb = None
    gpu_memory_used_mb = None
    cuda_probe = "env-hint"

    try:
        import torch  # type: ignore

        cuda_available = bool(torch.cuda.is_available())
        cuda_probe = "torch"
        if cuda_available:
            try:
                gpu_name = torch.cuda.get_device_name(0)
            except Exception:
                gpu_name = None
            try:
                memory_stats = torch.cuda.mem_get_info(0)
                if isinstance(memory_stats, tuple) and len(memory_stats) == 2:
                    free_bytes, total_bytes = memory_stats
                    gpu_memory_total_mb = round(float(total_bytes) / (1024 * 1024), 2)
                    gpu_memory_used_mb = round(float(total_bytes - free_bytes) / (1024 * 1024), 2)
            except Exception:
                gpu_memory_total_mb = None
                gpu_memory_used_mb = None
    except Exception:
        cuda_available = cuda_hint

    return {
        "cuda_available": cuda_available,
        "gpu_name": gpu_name,
        "gpu_memory_total_mb": gpu_memory_total_mb,
        "gpu_memory_used_mb": gpu_memory_used_mb,
        "cuda_probe": cuda_probe,
        "nvidia_visible_devices": visible_devices or None,
    }


async def _publish_worker_heartbeat(state: str, *, session_id: int | None = None) -> None:
    payload: dict[str, object] = {
        "state": state,
        "session_id": session_id,
        "pid": os.getpid(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "tryon_require_cuda": bool(settings.TRYON_REQUIRE_CUDA),
    }
    payload.update(_get_cuda_runtime_snapshot())
    try:
        await set_tryon_worker_heartbeat(payload)
    except Exception as exc:
        logger.debug("Failed to publish try-on worker heartbeat: %s", exc)


def _decode_data_url_image(data_url: str) -> bytes:
    return base64.b64decode(data_url.split(",", 1)[-1])


def _load_media_bytes(storage_key: str) -> bytes:
    local_file_path = build_local_media_path(storage_key)
    if local_file_path.exists():
        return local_file_path.read_bytes()
    file_bytes, _ = s3_client.get_file(storage_key)
    return file_bytes


def _open_image(image_bytes: bytes) -> Image.Image:
    image = Image.open(io.BytesIO(image_bytes))
    image.load()
    return image


def _build_result_storage_key(user_id: int, filename: str = "result.png") -> str:
    extension = os.path.splitext(filename)[1] or ".png"
    return f"user_{user_id}/tryon/result/{uuid.uuid4()}{extension}"


async def process_tryon_task(task: dict[str, object]) -> None:
    session_id = int(task["session_id"])
    user_id = int(task["user_id"])
    attempt = int(task.get("attempt", 0))
    tryon_repo = TryOnRepository()
    event_repo = TryOnEventRepository()
    media_repo = MediaRepository()
    use_case = TryOnUseCase(get_ootd_service())

    if not await acquire_tryon_processing_lock(session_id):
        logger.info("Try-on session %s is already being processed, skipping duplicate task", session_id)
        return

    try:
        _release_cuda_memory()
        async with AsyncSessionLocal() as db:
            session = await tryon_repo.get(db, session_id)
            if session is None:
                logger.warning("Try-on session %s not found, skipping task", session_id)
                return

            avatar_media = await media_repo.get(db, int(task["avatar_media_id"]))
            cloth_media = await media_repo.get(db, int(task["cloth_media_id"]))
            if avatar_media is None or cloth_media is None:
                await tryon_repo.update_status(
                    db,
                    session_id,
                    TryOnStatus.FAILED,
                    error_text="Input media not found for try-on task",
                )
                await event_repo.create_event(
                    db,
                    session_id=session_id,
                    event_type=TryOnEventType.FAILED,
                    attempt=attempt,
                    error_text="Input media not found for try-on task",
                    details="Worker could not find input media",
                )
                return

            await tryon_repo.update_status(db, session_id, TryOnStatus.PROCESSING)
            await event_repo.create_event(
                db,
                session_id=session_id,
                event_type=TryOnEventType.PROCESSING,
                attempt=attempt,
                details="Worker started processing try-on task",
            )

            model_bytes = _load_media_bytes(avatar_media.storage_key)
            cloth_bytes = _load_media_bytes(cloth_media.storage_key)

            cache_key = build_tryon_cache_key(
                model_bytes=model_bytes,
                cloth_bytes=cloth_bytes,
                model_type=str(task["model_type"]),
                category=int(task["category"]),
                scale=float(task["scale"]),
                num_steps=int(task["num_steps"]),
                num_samples=int(task["num_samples"]),
                seed=int(task["seed"]),
            )
            cached_result = await get_cached_tryon_result(cache_key)
            if cached_result and cached_result.get("result_media_id") is not None:
                await tryon_repo.update_status(
                    db,
                    session_id,
                    TryOnStatus.COMPLETED,
                    result_media_id=int(cached_result["result_media_id"]),
                )
                await event_repo.create_event(
                    db,
                    session_id=session_id,
                    event_type=TryOnEventType.COMPLETED,
                    attempt=attempt,
                    details="Worker used cached try-on result",
                )
                return

            request = TryOnRequest(
                model_image=_open_image(model_bytes),
                cloth_image=_open_image(cloth_bytes),
                model_type=str(task["model_type"]),
                category=int(task["category"]),
                scale=float(task["scale"]),
                num_steps=int(task["num_steps"]),
                num_samples=int(task["num_samples"]),
                seed=int(task["seed"]),
            )
            result = use_case.execute(request)
            result_media_id = None
            result_urls = result.results

            if result.results:
                result_bytes = _decode_data_url_image(result.results[0])
                result_media = await media_repo.create_with_upload(
                    db,
                    file_content=result_bytes,
                    file_key=_build_result_storage_key(user_id),
                    kind=MediaType.IMAGE,
                    owner_user_id=user_id,
                    content_type="image/png",
                )
                result_media_id = result_media.id
                result_urls = [_media_file_url(result_media_id)] if result_media_id else result.results

            await tryon_repo.update_status(
                db,
                session_id,
                TryOnStatus.COMPLETED,
                result_media_id=result_media_id,
            )
            await event_repo.create_event(
                db,
                session_id=session_id,
                event_type=TryOnEventType.COMPLETED,
                attempt=attempt,
                details="Worker completed try-on task",
            )
            await cache_tryon_result(
                cache_key,
                results=result_urls,
                result_media_id=result_media_id,
            )
    except Exception as exc:
        logger.exception("Try-on worker failed for session %s (attempt %s)", session_id, attempt)
        is_non_retriable = _is_non_retriable_tryon_error(exc)
        if not is_non_retriable and attempt < settings.TRYON_QUEUE_MAX_RETRIES:
            retry_task = dict(task)
            retry_task["attempt"] = attempt + 1
            await enqueue_tryon_task(retry_task)
            async with AsyncSessionLocal() as db:
                await event_repo.create_event(
                    db,
                    session_id=session_id,
                    event_type=TryOnEventType.RETRY,
                    attempt=attempt + 1,
                    error_text=str(exc),
                    details="Requeued try-on task for retry",
                )
            logger.info(
                "Requeued try-on session %s for retry %s of %s",
                session_id,
                attempt + 1,
                settings.TRYON_QUEUE_MAX_RETRIES,
            )
            return

        await enqueue_tryon_dead_letter(dict(task), str(exc))
        async with AsyncSessionLocal() as db:
            await event_repo.create_event(
                db,
                session_id=session_id,
                event_type=TryOnEventType.DEAD_LETTERED,
                attempt=attempt,
                error_text=str(exc),
                details=(
                    "Moved try-on task to dead-letter queue (non-retriable error)"
                    if is_non_retriable
                    else "Moved try-on task to dead-letter queue"
                ),
            )
            await tryon_repo.update_status(
                db,
                session_id,
                TryOnStatus.FAILED,
                error_text=str(exc),
            )
            await event_repo.create_event(
                db,
                session_id=session_id,
                event_type=TryOnEventType.FAILED,
                attempt=attempt,
                error_text=str(exc),
                details="Worker marked try-on session as failed",
            )
    finally:
        await release_tryon_processing_lock(session_id)
        _release_cuda_memory()


async def run_tryon_worker() -> None:
    await ensure_schema_compatibility(engine)
    logger.info("Try-on worker started. Queue: %s", settings.TRYON_QUEUE_NAME)
    while True:
        await _publish_worker_heartbeat("idle")
        await maybe_run_periodic_tryon_recovery()
        await maybe_run_periodic_tryon_cleanup()
        task = await dequeue_tryon_task()
        if task is None:
            continue
        raw_session_id = task.get("session_id")
        session_id = int(raw_session_id) if raw_session_id is not None else None
        await _publish_worker_heartbeat("processing", session_id=session_id)
        await process_tryon_task(task)
        await _publish_worker_heartbeat("idle")
        await asyncio.sleep(0)
