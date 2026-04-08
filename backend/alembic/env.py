import asyncio

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context as alembic_context
from app.core.config import settings
from app.infrastructure.db.db import Base
from app.infrastructure.persistence.models import feed, garment, likes, media, tryon, tryon_event, user

config = getattr(alembic_context, "config")
target_metadata = Base.metadata
MODEL_MODULES = (feed, garment, likes, media, tryon, tryon_event, user)


def get_database_url() -> str:
    return settings.async_database_url


def run_migrations_offline() -> None:
    url = get_database_url()
    getattr(alembic_context, "configure")(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with getattr(alembic_context, "begin_transaction")():
        getattr(alembic_context, "run_migrations")()


def do_run_migrations(connection: Connection) -> None:
    getattr(alembic_context, "configure")(connection=connection, target_metadata=target_metadata)
    with getattr(alembic_context, "begin_transaction")():
        getattr(alembic_context, "run_migrations")()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        {"sqlalchemy.url": get_database_url()},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(run_async_migrations())
    finally:
        loop.close()
        asyncio.set_event_loop(None)


if getattr(alembic_context, "is_offline_mode")():
    run_migrations_offline()
else:
    run_migrations_online()
