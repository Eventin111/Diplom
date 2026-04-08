"""Alembic helper entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from app.core.config import settings

PROJECT_ROOT = Path(__file__).parent


def _build_alembic_config() -> Config:
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.async_database_url)
    return alembic_cfg


def run_migrations_online() -> None:
    print("Applying DB migrations...")
    command.upgrade(_build_alembic_config(), "head")
    print("Migrations applied successfully.")


def create_migration(revision_message: str) -> None:
    command.revision(_build_alembic_config(), message=revision_message, autogenerate=True)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        revision_message = sys.argv[2] if len(sys.argv) > 2 else "auto migration"
        create_migration(revision_message)
        print(f"Migration created: {revision_message}")
        return

    run_migrations_online()


if __name__ == "__main__":
    main()
