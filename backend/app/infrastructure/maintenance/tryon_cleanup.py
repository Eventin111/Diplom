from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.infrastructure.db.db import AsyncSessionLocal
from app.infrastructure.persistence.repositories.media_repo import MediaRepository
from app.infrastructure.persistence.repositories.tryon_event_repo import TryOnEventRepository
from app.infrastructure.persistence.repositories.tryon_repo import TryOnRepository
from app.infrastructure.queue.tryon_queue import delete_tryon_runtime_artifacts, trim_tryon_dead_letter_queue

_last_cleanup_run_at = 0.0


async def run_tryon_cleanup(*, force: bool = False) -> dict[str, int | bool]:
    tryon_repo = TryOnRepository()
    event_repo = TryOnEventRepository()
    media_repo = MediaRepository()
    older_than = datetime.now(timezone.utc) - timedelta(days=max(int(settings.TRYON_RETENTION_DAYS), 1))
    batch_size = max(int(settings.TRYON_CLEANUP_BATCH_SIZE), 1)

    async with AsyncSessionLocal() as db:
        sessions = await tryon_repo.get_cleanup_candidates(
            db,
            older_than=older_than,
            limit=batch_size,
        )
        session_ids = [session.id for session in sessions]
        media_ids = sorted(
            {
                media_id
                for session in sessions
                for media_id in (session.avatar_media_id, session.cloth_media_id, session.result_media_id)
                if media_id is not None
            }
        )
        media_assets = await media_repo.get_by_ids(db, media_ids)

        deleted_events = await event_repo.delete_by_session_ids(db, session_ids)
        deleted_sessions = await tryon_repo.delete_many(db, session_ids)
        deleted_media = await media_repo.delete_many(db, media_ids)

    storage_deleted = 0
    for media in media_assets:
        delete_result = media_repo.delete_storage(media.storage_key)
        if delete_result["local_deleted"] or delete_result["s3_deleted"]:
            storage_deleted += 1

    for session_id in session_ids:
        await delete_tryon_runtime_artifacts(session_id)

    dead_letter_removed = await trim_tryon_dead_letter_queue(settings.TRYON_DEAD_LETTER_MAX_ITEMS)

    return {
        "ran": True,
        "forced": force,
        "deleted_events": deleted_events,
        "deleted_sessions": deleted_sessions,
        "deleted_media_records": deleted_media,
        "deleted_storage_items": storage_deleted,
        "deleted_runtime_keys": len(session_ids),
        "trimmed_dead_letters": dead_letter_removed,
    }


async def maybe_run_periodic_tryon_cleanup() -> dict[str, int | bool]:
    global _last_cleanup_run_at

    interval_seconds = max(int(settings.TRYON_CLEANUP_INTERVAL_SECONDS), 1)
    now = time.time()
    if now - _last_cleanup_run_at < interval_seconds:
        return {
            "ran": False,
            "deleted_events": 0,
            "deleted_sessions": 0,
            "deleted_media_records": 0,
            "deleted_storage_items": 0,
            "deleted_runtime_keys": 0,
            "trimmed_dead_letters": 0,
        }

    _last_cleanup_run_at = now
    return await run_tryon_cleanup(force=False)
