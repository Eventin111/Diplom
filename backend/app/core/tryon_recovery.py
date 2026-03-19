from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.core.tryon_queue import (
    enqueue_tryon_task,
    get_tryon_task_snapshot,
    has_tryon_processing_lock,
)
from app.repositories.tryon_repo import TryOnRepository
from app.schemas.tryon import TryOnStatus


_last_recovery_run_at = 0.0


async def run_tryon_recovery(*, force: bool = False) -> dict[str, object]:
    tryon_repo = TryOnRepository()
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=settings.TRYON_STALE_PROCESSING_THRESHOLD_SECONDS)

    async with AsyncSessionLocal() as db:
        stale_sessions = await tryon_repo.get_stale_processing_sessions(db, older_than=cutoff)

        recovered_session_ids: list[int] = []
        skipped: list[dict[str, object]] = []

        for session in stale_sessions:
            if await has_tryon_processing_lock(session.id):
                skipped.append({"session_id": session.id, "reason": "processing lock is still active"})
                continue

            task_snapshot = await get_tryon_task_snapshot(session.id)
            if task_snapshot is None:
                skipped.append({"session_id": session.id, "reason": "task snapshot not found"})
                continue

            task_snapshot["attempt"] = 0
            await tryon_repo.update_status(db, session.id, TryOnStatus.QUEUED, error_text=None)
            await enqueue_tryon_task(task_snapshot)
            recovered_session_ids.append(session.id)

    return {
        "ran": True,
        "forced": force,
        "recovered_session_ids": recovered_session_ids,
        "skipped": skipped,
        "stale_threshold_seconds": settings.TRYON_STALE_PROCESSING_THRESHOLD_SECONDS,
    }


async def maybe_run_periodic_tryon_recovery() -> dict[str, object]:
    global _last_recovery_run_at

    interval_seconds = max(int(settings.TRYON_RECOVERY_INTERVAL_SECONDS), 1)
    now = time.time()
    if now - _last_recovery_run_at < interval_seconds:
        return {
            "ran": False,
            "recovered_session_ids": [],
            "skipped": [],
            "stale_threshold_seconds": settings.TRYON_STALE_PROCESSING_THRESHOLD_SECONDS,
        }

    _last_recovery_run_at = now
    return await run_tryon_recovery(force=False)
