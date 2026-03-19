from __future__ import annotations

import hashlib
import json
from typing import Any, Optional

from app.core.config import settings
from app.core.redis_client import get_redis_client


def build_tryon_cache_key(
    *,
    model_bytes: bytes,
    cloth_bytes: bytes,
    model_type: str,
    category: int,
    scale: float,
    num_steps: int,
    num_samples: int,
    seed: int,
) -> str:
    payload = json.dumps(
        {
            "model_type": model_type,
            "category": category,
            "scale": scale,
            "num_steps": num_steps,
            "num_samples": num_samples,
            "seed": seed,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = hashlib.sha256()
    digest.update(payload)
    digest.update(model_bytes)
    digest.update(cloth_bytes)
    return f"tryon:result:{digest.hexdigest()}"


async def get_cached_tryon_result(cache_key: str) -> Optional[dict[str, Any]]:
    try:
        raw_value = await get_redis_client().get(cache_key)
    except Exception:
        return None

    if not raw_value:
        return None

    try:
        payload = json.loads(raw_value)
    except json.JSONDecodeError:
        return None

    return payload if isinstance(payload, dict) else None


async def cache_tryon_result(
    cache_key: str,
    *,
    results: list[str],
    result_media_id: Optional[int],
    ttl_seconds: Optional[int] = None,
) -> None:
    payload = json.dumps(
        {
            "results": results,
            "result_media_id": result_media_id,
        },
        separators=(",", ":"),
    )

    try:
        await get_redis_client().setex(
            cache_key,
            ttl_seconds or settings.TRYON_CACHE_TTL_SECONDS,
            payload,
        )
    except Exception:
        return
