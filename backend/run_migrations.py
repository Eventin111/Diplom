import asyncio
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from alembic.config import Config
from alembic import command
from app.core.config import settings

def run_migrations_online():
    """Запуск миграций с правильной конфигурацией"""
    
    print("🔄 Применение миграций базы данных...")
    
    # Создаем конфиг Alembic программно
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(project_root / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.async_database_url)
    
    # Запускаем миграцию
    command.upgrade(alembic_cfg, "head")
    print("✅ Миграции применены успешно!")

def create_migration(message: str):
    """Создание новой миграции"""
    alembic_cfg = Config()
    alembic_cfg.set_main_option("script_location", str(project_root / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", settings.async_database_url)
    
    command.revision(alembic_cfg, message=message, autogenerate=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "create":
        message = sys.argv[2] if len(sys.argv) > 2 else "auto migration"
        create_migration(message)
        print(f"Миграция создана: {message}")
    else:
        run_migrations_online()