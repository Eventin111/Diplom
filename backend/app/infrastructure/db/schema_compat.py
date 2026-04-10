from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


async def _table_exists(conn, table_name: str) -> bool:
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = :table_name
            )
            """
        ),
        {"table_name": table_name},
    )
    return bool(result.scalar())


async def _column_exists(conn, table_name: str, column_name: str) -> bool:
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = :table_name
                  AND column_name = :column_name
            )
            """
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    return bool(result.scalar())


async def ensure_schema_compatibility(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        if await _table_exists(conn, "tryon_sessions"):
            if not await _column_exists(conn, "tryon_sessions", "cloth_media_id"):
                await conn.execute(text("ALTER TABLE tryon_sessions ADD COLUMN cloth_media_id INTEGER NULL"))

            if not await _column_exists(conn, "tryon_sessions", "result_media_id"):
                await conn.execute(text("ALTER TABLE tryon_sessions ADD COLUMN result_media_id INTEGER NULL"))

            if not await _column_exists(conn, "tryon_sessions", "error_text"):
                await conn.execute(text("ALTER TABLE tryon_sessions ADD COLUMN error_text VARCHAR(1024) NULL"))

        await conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS tryon_events (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL REFERENCES tryon_sessions(id),
                    event_type VARCHAR(64) NOT NULL,
                    attempt INTEGER NULL,
                    error_text VARCHAR(1024) NULL,
                    details VARCHAR(1024) NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NULL
                )
                """
            )
        )
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tryon_events_session_id ON tryon_events (session_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_tryon_events_event_type ON tryon_events (event_type)"))
