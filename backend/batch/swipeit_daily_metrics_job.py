"""
Batch job for daily SwipeIt metrics.

Idempotency:
- metric_date is a primary key in daily_project_metrics
- aggregate mode performs UPSERT for the same metric_date
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Iterable

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


@dataclass(frozen=True)
class DailyProjectMetrics:
    metric_date: date
    users_registered_count: int
    feed_items_created_count: int
    likes_created_count: int
    tryon_total_count: int
    tryon_successful_count: int
    tryon_interrupted_count: int


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compute or validate daily SwipeIt metrics")
    parser.add_argument(
        "--run-date",
        required=True,
        help="Logical execution date in YYYY-MM-DD format (Airflow ds)",
    )
    parser.add_argument(
        "--mode",
        choices=["aggregate", "validate"],
        default="aggregate",
        help="aggregate: compute+upsert metrics, validate: ensure row exists for run-date",
    )
    parser.add_argument(
        "--db-url",
        default=os.getenv("BATCH_DB_URL") or os.getenv("DB_URL"),
        help="PostgreSQL URL. Can also be set via BATCH_DB_URL or DB_URL.",
    )
    parser.add_argument(
        "--interrupted-statuses",
        default=os.getenv("TRYON_INTERRUPTED_STATUSES", "failed"),
        help="Comma-separated try-on statuses treated as interrupted (default: failed).",
    )
    args = parser.parse_args()
    if not args.db_url:
        parser.error("PostgreSQL URL is required. Pass --db-url or set BATCH_DB_URL/DB_URL.")
    return args


def _to_async_db_url(db_url: str) -> str:
    if db_url.startswith("postgresql+asyncpg://"):
        return db_url
    if db_url.startswith("postgresql://"):
        return db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if db_url.startswith("postgres://"):
        return db_url.replace("postgres://", "postgresql+asyncpg://", 1)
    raise ValueError("Unsupported DB URL. Expected postgresql://...")


def _build_utc_day_window(metric_day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(metric_day, time.min).replace(tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return start, end


def _parse_statuses_csv(raw: str) -> tuple[str, ...]:
    statuses = tuple(sorted({part.strip().lower() for part in str(raw).split(",") if part.strip()}))
    if not statuses:
        raise ValueError("Interrupted statuses list cannot be empty")
    return statuses


async def _ensure_target_table(conn) -> None:
    await conn.execute(
        text("SELECT pg_advisory_xact_lock(hashtext('daily_project_metrics_table_lock'));")
    )
    await conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS daily_project_metrics (
                metric_date DATE PRIMARY KEY,
                users_registered_count INTEGER NOT NULL,
                feed_items_created_count INTEGER NOT NULL,
                likes_created_count INTEGER NOT NULL,
                tryon_total_count INTEGER NOT NULL,
                tryon_successful_count INTEGER NOT NULL,
                tryon_interrupted_count INTEGER NOT NULL,
                generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )
    )


async def _ensure_source_tables(conn, table_names: Iterable[str]) -> None:
    rows = await conn.execute(
        text(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = ANY(:table_names)
            """
        ),
        {"table_names": list(table_names)},
    )
    existing = {str(name) for (name,) in rows.fetchall()}
    missing = sorted(set(table_names) - existing)
    if missing:
        raise RuntimeError(f"Missing source tables for metrics job: {', '.join(missing)}")


async def _count_by_day(conn, table_name: str, window_start: datetime, window_end: datetime) -> int:
    result = await conn.execute(
        text(
            f"""
            SELECT COUNT(*)::int AS cnt
            FROM {table_name}
            WHERE created_at >= :window_start
              AND created_at < :window_end
            """
        ),
        {"window_start": window_start, "window_end": window_end},
    )
    return int(result.scalar_one())


async def _collect_metrics(
    conn,
    metric_day: date,
    interrupted_statuses: tuple[str, ...],
) -> DailyProjectMetrics:
    window_start, window_end = _build_utc_day_window(metric_day)

    users_count = await _count_by_day(conn, "users", window_start, window_end)
    feed_items_count = await _count_by_day(conn, "feed_items", window_start, window_end)
    likes_count = await _count_by_day(conn, "likes", window_start, window_end)

    tryon_rows = await conn.execute(
        text(
            """
            SELECT status, COUNT(*)::int AS cnt
            FROM tryon_sessions
            WHERE created_at >= :window_start
              AND created_at < :window_end
            GROUP BY status
            """
        ),
        {"window_start": window_start, "window_end": window_end},
    )
    raw_tryon = {str(status): int(cnt) for status, cnt in tryon_rows.fetchall()}
    tryon_successful_count = raw_tryon.get("completed", 0)
    tryon_interrupted_count = sum(raw_tryon.get(status, 0) for status in interrupted_statuses)
    tryon_total_count = sum(raw_tryon.values())

    return DailyProjectMetrics(
        metric_date=metric_day,
        users_registered_count=users_count,
        feed_items_created_count=feed_items_count,
        likes_created_count=likes_count,
        tryon_total_count=tryon_total_count,
        tryon_successful_count=tryon_successful_count,
        tryon_interrupted_count=tryon_interrupted_count,
    )


async def _upsert_metrics(conn, metrics: DailyProjectMetrics) -> None:
    await conn.execute(
        text(
            """
            INSERT INTO daily_project_metrics (
                metric_date,
                users_registered_count,
                feed_items_created_count,
                likes_created_count,
                tryon_total_count,
                tryon_successful_count,
                tryon_interrupted_count,
                generated_at,
                updated_at
            )
            VALUES (
                :metric_date,
                :users_registered_count,
                :feed_items_created_count,
                :likes_created_count,
                :tryon_total_count,
                :tryon_successful_count,
                :tryon_interrupted_count,
                NOW(),
                NOW()
            )
            ON CONFLICT (metric_date) DO UPDATE
            SET
                users_registered_count = EXCLUDED.users_registered_count,
                feed_items_created_count = EXCLUDED.feed_items_created_count,
                likes_created_count = EXCLUDED.likes_created_count,
                tryon_total_count = EXCLUDED.tryon_total_count,
                tryon_successful_count = EXCLUDED.tryon_successful_count,
                tryon_interrupted_count = EXCLUDED.tryon_interrupted_count,
                updated_at = NOW();
            """
        ),
        {
            "metric_date": metrics.metric_date,
            "users_registered_count": metrics.users_registered_count,
            "feed_items_created_count": metrics.feed_items_created_count,
            "likes_created_count": metrics.likes_created_count,
            "tryon_total_count": metrics.tryon_total_count,
            "tryon_successful_count": metrics.tryon_successful_count,
            "tryon_interrupted_count": metrics.tryon_interrupted_count,
        },
    )


async def _validate_metrics_row(conn, metric_day: date) -> dict[str, int | str]:
    result = await conn.execute(
        text(
            """
            SELECT
                metric_date,
                users_registered_count,
                feed_items_created_count,
                likes_created_count,
                tryon_total_count,
                tryon_successful_count,
                tryon_interrupted_count
            FROM daily_project_metrics
            WHERE metric_date = :metric_date
            """
        ),
        {"metric_date": metric_day},
    )
    row = result.mappings().first()
    if row is None:
        raise RuntimeError(f"Row for metric_date={metric_day.isoformat()} does not exist")

    total = int(row["tryon_total_count"])
    completed = int(row["tryon_successful_count"])
    interrupted = int(row["tryon_interrupted_count"])
    if total < completed + interrupted:
        raise RuntimeError(
            "Inconsistent metrics row: tryon_total_count is lower than "
            "tryon_successful_count + tryon_interrupted_count"
        )

    return {
        "metric_date": row["metric_date"].isoformat(),
        "users_registered_count": int(row["users_registered_count"]),
        "feed_items_created_count": int(row["feed_items_created_count"]),
        "likes_created_count": int(row["likes_created_count"]),
        "tryon_total_count": int(row["tryon_total_count"]),
        "tryon_successful_count": int(row["tryon_successful_count"]),
        "tryon_interrupted_count": int(row["tryon_interrupted_count"]),
    }


async def run_aggregate(
    run_day: date,
    db_url: str,
    interrupted_statuses: tuple[str, ...],
) -> DailyProjectMetrics:
    engine = create_async_engine(_to_async_db_url(db_url), pool_pre_ping=True, future=True)
    try:
        async with engine.begin() as conn:
            await _ensure_source_tables(conn, ("users", "feed_items", "likes", "tryon_sessions"))
            await _ensure_target_table(conn)
            metrics = await _collect_metrics(conn, run_day, interrupted_statuses=interrupted_statuses)
            await _upsert_metrics(conn, metrics)
            return metrics
    finally:
        await engine.dispose()


async def run_validate(run_day: date, db_url: str) -> dict[str, int | str]:
    engine = create_async_engine(_to_async_db_url(db_url), pool_pre_ping=True, future=True)
    try:
        async with engine.begin() as conn:
            await _ensure_target_table(conn)
            return await _validate_metrics_row(conn, run_day)
    finally:
        await engine.dispose()


def main() -> None:
    args = _parse_args()
    run_day = datetime.strptime(args.run_date, "%Y-%m-%d").date()
    interrupted_statuses = _parse_statuses_csv(args.interrupted_statuses)

    if args.mode == "aggregate":
        metrics = asyncio.run(
            run_aggregate(
                run_day,
                args.db_url,
                interrupted_statuses=interrupted_statuses,
            )
        )
        print(
            json.dumps(
                {
                    "mode": "aggregate",
                    "metric_date": metrics.metric_date.isoformat(),
                    "users_registered_count": metrics.users_registered_count,
                    "feed_items_created_count": metrics.feed_items_created_count,
                    "likes_created_count": metrics.likes_created_count,
                    "tryon_total_count": metrics.tryon_total_count,
                    "tryon_successful_count": metrics.tryon_successful_count,
                    "tryon_interrupted_count": metrics.tryon_interrupted_count,
                    "interrupted_statuses": list(interrupted_statuses),
                },
                ensure_ascii=False,
            )
        )
        return

    validated_row = asyncio.run(run_validate(run_day, args.db_url))
    print(
        json.dumps(
            {
                "mode": "validate",
                "status": "ok",
                "row": validated_row,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
