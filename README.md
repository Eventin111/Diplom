# SwipeIt 

<img width="1536" height="1024" alt="image" src="https://github.com/Eventin111/Diplom/blob/Frontend-Backend-ML/image/SwipeIt.png" />

SwipeIt — это веб-платформа социальной сети, посвящённой моде, стилю и обмену образами. Пользователи могут публиковать свои луки, вдохновляться стилями других людей и взаимодействовать с модным сообществом.

В рамках развития платформы в сервис интегрируется функция виртуальной примерки одежды на основе технологий искусственного интеллекта. Новый модуль позволяет пользователям примерять одежду прямо в браузере, используя модели компьютерного зрения и машинного обучения для реалистичного наложения одежды на изображение пользователя.

Интеграция виртуальной примерки расширяет возможности платформы, объединяя социальное взаимодействие и e-commerce. Пользователи могут не только делиться образами и получать вдохновение, но и экспериментировать со стилем, примеряя одежду перед покупкой.

<img width="1536" height="1024" alt="image" src="https://github.com/Eventin111/Diplom/blob/Frontend-Backend-ML/image/Идея.png" />

## Основные возможности платформы

- социальная лента модных образов (UGC)
- публикация и обсуждение луков
- взаимодействие пользователей внутри fashion-сообщества
- персонализированные рекомендации стиля
- виртуальная примерка одежды на основе AI
- интеграция с брендами и e-commerce платформами

## Технологии

- Python / FastAPI
- PyTorch
- Computer Vision / Deep Learning
- Web frontend (React / Web stack)
- AI Try-On models (VITON / diffusion approaches)

## Архитектура ML-системы

<img width="1536" height="1024" alt="image" src="https://github.com/Eventin111/Diplom/blob/Frontend-Backend-ML/image/Примерка.png" />

Функция виртуальной примерки реализована как ML-модуль, интегрированный в веб-платформу SwipeIt. Система включает:

- пайплайн обработки изображений пользователя
- модель виртуальной примерки одежды
- API для взаимодействия с фронтендом
- систему хранения и обработки данных

## Цель проекта

Расширить возможности социальной платформы SwipeIt за счёт внедрения технологий искусственного интеллекта, позволяющих пользователям примерять одежду онлайн, получать вдохновение от сообщества и принимать более уверенные решения при выборе стиля и покупке одежды.

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/Eventin111/Diplom.git
cd Diplom
```

### 2. Создание окружения со всеми зависимостями

```bash
conda env create -f environment.yml
conda activate ootd
```

Окружение уже включает Python `3.10`, backend + ML зависимости и Node.js `18`.

### 3. Настройка окружения

Создай `.env` на основе шаблона:

```bash
cp .env.example .env
```

Заполни в `.env` секреты и пароли (`CHANGE_ME_...`), затем проверь ключевые переменные:

```env
DB_URL=postgresql://postgres:CHANGE_ME_DB_PASSWORD@localhost:5433/swipeit
SECRET_KEY=CHANGE_ME_SECRET_KEY
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=CHANGE_ME_S3_ACCESS_KEY
S3_SECRET_KEY=CHANGE_ME_S3_SECRET_KEY
S3_BUCKET_NAME=swipeit-media
S3_REGION=us-east-1
S3_SECURE=false
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=["http://localhost:3000"]
ACCESS_TOKEN_EXPIRE_MINUTES=60
POSTGRES_PASSWORD=CHANGE_ME_DB_PASSWORD
MINIO_ROOT_USER=CHANGE_ME_MINIO_USER
MINIO_ROOT_PASSWORD=CHANGE_ME_MINIO_PASSWORD
```

Единая схема хранения и прокидывания секретов (local + GitHub + Airflow):

- `docs/secret-store.md`

### 4. Запуск БД, MinIO и Redis

```bash
docker-compose up -d postgres minio redis
```

После запуска будут доступны:

- PostgreSQL: `localhost:5433`
- MinIO API: `http://localhost:9000`
- MinIO Console: `http://localhost:9001`
- Redis: `localhost:6379`

### 5. Запуск backend

```bash
cd backend
conda run -n ootd python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- Backend: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

### 5.1 Backend service (uv + Docker + CI/CD)

- pin зависимостей backend: `backend/pyproject.toml` + `backend/uv.lock`
- локальная синхронизация зависимостей: `uv sync --project backend --frozen --group dev`
- Dockerfile сервиса: `backend/Dockerfile`
- CI линтеров/тестов: `.github/workflows/ci.yml`
- CD push-модель деплоя на удалённый сервер: `.github/workflows/deploy-backend.yml`
- registry образов: `ghcr.io/<owner>/diplom-backend`

### 6. Запуск frontend

Установи frontend-зависимости один раз:

```bash
cd frontend
conda run -n ootd npm install
```

Для разработки:

```bash
conda run -n ootd npm start
```

- Dev frontend: `http://localhost:3000`

Если нужен более стабильный запуск без hot reload:

```bash
conda run -n ootd npm run build
conda run -n ootd npx serve -s build -l 4173
```

- Stable frontend: `http://localhost:4173`

### 7. Что сейчас сохраняется в БД

В PostgreSQL сохраняются:

- пользователи: таблица `users`
- загруженные изображения: таблица `media_assets`
- лайки: таблица `likes`
- сессии примерки: таблица `tryon_sessions`
- элементы ленты: таблица `feed_items`

## 👗 Virtual Try-On

### Установка ML зависимостей

```bash
pip install torch==2.0.1 torchvision==0.15.2
```

### Загрузка моделей

```bash
cd ml
python scripts/download_models.py
```

### API

```
POST /api/v1/tryon
```

Параметры (multipart/form-data):
- `person_image` — фото человека
- `cloth_image` — фото одежды
- `model_type` — `hd` (полутело) или `dc` (полное тело)

## 📁 Структура

```text
Diplom/
├── backend/           # FastAPI
│   ├── app/api/v1/    # Endpoints
│   ├── run_server.py
│   └── app/core/config.py
├── ml/                # OOTDiffusion
│   ├── swipeit_ml/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   │   ├── adapters/
│   │   │   ├── config/
│   │   │   └── runtime/
│   │   └── presentation/
│   ├── third_party/   # Vendor OOTDiffusion/OpenPose/HumanParsing
│   ├── examples/      # Demo assets
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   └── scripts/       # Служебные утилиты
├── frontend/          # React frontend
│   ├── src/core/      # Clean Architecture (domain/app/infra)
│   ├── src/config/    # Конфигурация фронта
│   ├── src/pages/
│   └── src/components/
├── docker-compose.yml
└── requirements.txt
```

## ⚠️ Требования

| Режим | RAM |
|-------|-----|
| CPU (half-body) | 8GB+ |
| CPU (full-body) | 16GB+ |

## 📝 Лицензия

MIT

## 📊 Batch сервис (Airflow)

Для ежедневной аналитики платформы добавлен DAG:

- `batch/airflow/dags/swipeit_daily_metrics_dag.py`
- используются шаги `DockerOperator`: `build_daily_metrics` и `validate_daily_metrics`
- считает суточные метрики по `users`, `feed_items`, `likes`, `tryon_sessions`
- результат пишет в `daily_project_metrics` через идемпотентный `UPSERT` по `metric_date`
- поддерживает `catchup/backfill`

Подробная инструкция запуска и backfill:

- `batch/airflow/README.md`
