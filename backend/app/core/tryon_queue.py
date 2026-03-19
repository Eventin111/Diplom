from __future__ import annotations

import json
from typing import Any, Optional

from app.core.config import settings
from app.core.redis_client import get_redis_client


def build_tryon_task_payload(
    *,
    session_id: int,
    user_id: int,
    avatar_media_id: int,
    cloth_media_id: int,
    model_type: str,
    category: int,
    scale: float,
    num_steps: int,
    num_samples: int,
    seed: int,
    attempt: int = 0,
) -> dict[str, Any]:
    return {
        "session_id": session_id,
        "user_id": user_id,
        "avatar_media_id": avatar_media_id,
        "cloth_media_id": cloth_media_id,
        "model_type": model_type,
        "category": category,
        "scale": scale,
        "num_steps": num_steps,
        "num_samples": num_samples,
        "seed": seed,
        "attempt": attempt,
    }


async def enqueue_tryon_task(task: dict[str, Any]) -> None:
    await get_redis_client().lpush(settings.TRYON_QUEUE_NAME, json.dumps(task, separators=(",", ":")))


async def dequeue_tryon_task(timeout_seconds: Optional[int] = None) -> Optional[dict[str, Any]]:
    timeout = timeout_seconds if timeout_seconds is not None else settings.TRYON_QUEUE_BLOCK_TIMEOUT_SECONDS
    item = await get_redis_client().brpop(settings.TRYON_QUEUE_NAME, timeout=timeout)
    if item is None:
        return None

    _, raw_payload = item
    payload = json.loads(raw_payload)
    return payload if isinstance(payload, dict) else None


async def get_tryon_queue_length() -> int:
    return int(await get_redis_client().llen(settings.TRYON_QUEUE_NAME))


async def get_tryon_queue_health() -> dict[str, Any]:
    redis_client = get_redis_client()
    redis_ok = bool(await redis_client.ping())
    queue_length = int(await redis_client.llen(settings.TRYON_QUEUE_NAME))
    dead_letter_queue_length = int(await redis_client.llen(settings.TRYON_DEAD_LETTER_QUEUE_NAME))
    return {
        "redis_ok": redis_ok,
        "queue_name": settings.TRYON_QUEUE_NAME,
        "queue_length": queue_length,
        "dead_letter_queue_name": settings.TRYON_DEAD_LETTER_QUEUE_NAME,
        "dead_letter_queue_length": dead_letter_queue_length,
    }


def build_tryon_processing_lock_key(session_id: int) -> str:
    return f"tryon:processing:{session_id}"


async def acquire_tryon_processing_lock(session_id: int) -> bool:
    return bool(
        await get_redis_client().set(
            build_tryon_processing_lock_key(session_id),
            "1",
            ex=settings.TRYON_PROCESSING_LOCK_TTL_SECONDS,
            nx=True,
        )
    )


async def release_tryon_processing_lock(session_id: int) -> None:
    await get_redis_client().delete(build_tryon_processing_lock_key(session_id))


async def get_tryon_processing_lock_count() -> int:
    redis_client = get_redis_client()
    cursor = 0
    count = 0

    while True:
        cursor, keys = await redis_client.scan(cursor=cursor, match="tryon:processing:*", count=100)
        count += len(keys)
        if cursor == 0:
            break

    return count


async def enqueue_tryon_dead_letter(task: dict[str, Any], error_text: str) -> None:
    payload = {
        "task": task,
        "error_text": error_text,
    }
    await get_redis_client().lpush(
        settings.TRYON_DEAD_LETTER_QUEUE_NAME,
        json.dumps(payload, separators=(",", ":")),
    )


async def get_tryon_dead_letters(limit: int = 20) -> list[dict[str, Any]]:
    raw_items = await get_redis_client().lrange(settings.TRYON_DEAD_LETTER_QUEUE_NAME, 0, max(limit - 1, 0))
    items: list[dict[str, Any]] = []
    for raw_item in raw_items:
        payload = json.loads(raw_item)
        if isinstance(payload, dict):
            items.append(payload)
    return items
