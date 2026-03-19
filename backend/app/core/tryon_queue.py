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
