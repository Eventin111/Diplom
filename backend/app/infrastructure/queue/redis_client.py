from __future__ import annotations

from typing import Any, Optional

try:
    from redis.asyncio import Redis
except ModuleNotFoundError:  # pragma: no cover - fallback for partial environments
    Redis = Any

from app.core.config import settings


_redis_client: Optional[Redis] = None


def get_redis_client() -> Redis:
    global _redis_client
    if _redis_client is None:
        if Redis is Any:
            raise RuntimeError("redis package is not installed")
        _redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def close_redis_client() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
