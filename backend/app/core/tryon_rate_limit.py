from __future__ import annotations

import time

from fastapi import HTTPException, status

from app.core.config import settings
from app.core.redis_client import get_redis_client


def build_tryon_rate_limit_key(user_id: int, bucket: int) -> str:
    return f"tryon:ratelimit:user:{user_id}:{bucket}"


async def consume_tryon_rate_limit(user_id: int) -> dict[str, int | bool]:
    window_seconds = max(int(settings.TRYON_RATE_LIMIT_WINDOW_SECONDS), 1)
    limit = max(int(settings.TRYON_RATE_LIMIT_REQUESTS), 1)
    now = int(time.time())
    bucket = now // window_seconds
    key = build_tryon_rate_limit_key(user_id, bucket)

    redis_client = get_redis_client()
    current_count = int(await redis_client.incr(key))
    if current_count == 1:
        await redis_client.expire(key, window_seconds + 1)

    retry_after = max(window_seconds - (now % window_seconds), 1)

    return {
        "allowed": current_count <= limit,
        "limit": limit,
        "remaining": max(limit - current_count, 0),
        "retry_after": retry_after,
        "count": current_count,
        "window_seconds": window_seconds,
    }


async def enforce_tryon_rate_limit(user_id: int) -> None:
    rate_limit_state = await consume_tryon_rate_limit(user_id)
    if rate_limit_state["allowed"]:
        return

    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "message": "Try-on rate limit exceeded",
            "limit": rate_limit_state["limit"],
            "window_seconds": rate_limit_state["window_seconds"],
            "retry_after": rate_limit_state["retry_after"],
        },
        headers={"Retry-After": str(rate_limit_state["retry_after"])},
    )
