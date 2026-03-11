"""
Clean Architecture структура проекта SwipeIt

├── domain/           # Domain Layer - бизнес-сущности и правила
│   ├── entities/     # Сущности (User, Garment, etc.)
│   └── exceptions/   # Доменные исключения
│
├── application/      # Application Layer - use cases
│   ├── use_cases/    # Бизнес-логика
│   ├── services/     # Сервисы (в т.ч. ML)
│   ├── interfaces/   # Абстракции (порты)
│   └── dto/          # Data Transfer Objects
│
├── infrastructure/   # Infrastructure Layer - внешние системы
│   ├── database/     # Репозитории, миграции
│   ├── storage/      # MinIO/S3 хранилище
│   ├── ml/           # ML сервисы (OOTDiffusion)
│   └── auth/         # Аутентификация
│
└── presentation/     # Presentation Layer - API
    ├── api/          # FastAPI роутеры
    └── deps.py       # Зависимости
"""

from pathlib import Path
import sys

# Добавляем корневую папку для импортов
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
