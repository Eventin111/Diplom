from __future__ import annotations

import json
from typing import Any, Optional

from app.core.config import settings
from app.infrastructure.queue.redis_client import get_redis_client


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
    redis_client = get_redis_client()
    serialized_task = json.dumps(task, separators=(",", ":"))
    await redis_client.lpush(settings.TRYON_QUEUE_NAME, serialized_task)
    session_id = task.get("session_id")
    if session_id is not None:
        await redis_client.set(
            build_tryon_task_snapshot_key(int(session_id)),
            serialized_task,
            ex=settings.TRYON_TASK_SNAPSHOT_TTL_SECONDS,
        )


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


async def set_tryon_worker_heartbeat(payload: dict[str, Any]) -> None:
    await get_redis_client().set(
        settings.TRYON_WORKER_HEARTBEAT_KEY,
        json.dumps(payload, separators=(",", ":")),
        ex=settings.TRYON_WORKER_HEARTBEAT_TTL_SECONDS,
    )


async def get_tryon_worker_heartbeat() -> Optional[dict[str, Any]]:
    raw_payload = await get_redis_client().get(settings.TRYON_WORKER_HEARTBEAT_KEY)
    if raw_payload is None:
        return None
    payload = json.loads(raw_payload)
    return payload if isinstance(payload, dict) else None


def build_tryon_processing_lock_key(session_id: int) -> str:
    return f"tryon:processing:{session_id}"


def build_tryon_task_snapshot_key(session_id: int) -> str:
    return f"tryon:task:{session_id}"


def build_tryon_cancel_key(session_id: int) -> str:
    return f"tryon:cancel:{session_id}"


def build_tryon_runtime_pid_key(session_id: int) -> str:
    return f"tryon:runtime:pid:{session_id}"


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


async def has_tryon_processing_lock(session_id: int) -> bool:
    return bool(await get_redis_client().exists(build_tryon_processing_lock_key(session_id)))


async def request_tryon_cancellation(session_id: int) -> None:
    await get_redis_client().set(
        build_tryon_cancel_key(session_id),
        "1",
        ex=settings.TRYON_PROCESSING_LOCK_TTL_SECONDS,
    )


async def is_tryon_cancellation_requested(session_id: int) -> bool:
    return bool(await get_redis_client().exists(build_tryon_cancel_key(session_id)))


async def clear_tryon_cancellation(session_id: int) -> None:
    await get_redis_client().delete(build_tryon_cancel_key(session_id))


async def set_tryon_runtime_pid(session_id: int, pid: int) -> None:
    await get_redis_client().set(
        build_tryon_runtime_pid_key(session_id),
        str(pid),
        ex=settings.TRYON_PROCESSING_LOCK_TTL_SECONDS,
    )


async def clear_tryon_runtime_pid(session_id: int) -> None:
    await get_redis_client().delete(build_tryon_runtime_pid_key(session_id))


async def get_tryon_runtime_pid(session_id: int) -> Optional[int]:
    raw_pid = await get_redis_client().get(build_tryon_runtime_pid_key(session_id))
    if raw_pid is None:
        return None
    try:
        return int(raw_pid)
    except (TypeError, ValueError):
        return None


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
    for index, raw_item in enumerate(raw_items):
        payload = json.loads(raw_item)
        if isinstance(payload, dict):
            payload["index"] = index
            items.append(payload)
    return items


async def get_tryon_task_snapshot(session_id: int) -> Optional[dict[str, Any]]:
    raw_item = await get_redis_client().get(build_tryon_task_snapshot_key(session_id))
    if raw_item is None:
        return None
    payload = json.loads(raw_item)
    return payload if isinstance(payload, dict) else None


async def delete_tryon_runtime_artifacts(session_id: int) -> None:
    await get_redis_client().delete(
        build_tryon_task_snapshot_key(session_id),
        build_tryon_processing_lock_key(session_id),
        build_tryon_cancel_key(session_id),
        build_tryon_runtime_pid_key(session_id),
    )


async def trim_tryon_dead_letter_queue(max_items: int) -> int:
    normalized_max_items = max(int(max_items), 0)
    redis_client = get_redis_client()
    current_length = int(await redis_client.llen(settings.TRYON_DEAD_LETTER_QUEUE_NAME))
    if current_length <= normalized_max_items:
        return 0

    if normalized_max_items == 0:
        await redis_client.ltrim(settings.TRYON_DEAD_LETTER_QUEUE_NAME, 1, 0)
        return current_length

    await redis_client.ltrim(settings.TRYON_DEAD_LETTER_QUEUE_NAME, 0, normalized_max_items - 1)
    return current_length - normalized_max_items


async def requeue_tryon_dead_letter(index: int) -> dict[str, Any]:
    redis_client = get_redis_client()
    raw_item = await redis_client.lindex(settings.TRYON_DEAD_LETTER_QUEUE_NAME, index)
    if raw_item is None:
        raise IndexError("Dead-letter item not found")

    payload = json.loads(raw_item)
    if not isinstance(payload, dict) or not isinstance(payload.get("task"), dict):
        raise ValueError("Dead-letter item has invalid format")

    task = dict(payload["task"])
    task["attempt"] = 0

    tombstone = "__deleted__"
    await redis_client.lset(settings.TRYON_DEAD_LETTER_QUEUE_NAME, index, tombstone)
    await redis_client.lrem(settings.TRYON_DEAD_LETTER_QUEUE_NAME, 1, tombstone)
    await enqueue_tryon_task(task)

    return {
        "requeued_task": task,
        "previous_error_text": payload.get("error_text"),
        "requeued_from_index": index,
    }
