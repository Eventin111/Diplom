# Secret Store (GitHub + Airflow + Local)

## Цель

Секреты не должны храниться в git в открытом виде.  
Единая схема проекта:

1. Локально: `.env` (в `.gitignore`).
2. GitHub: `Settings -> Secrets and variables -> Actions`.
3. Airflow: `AIRFLOW_CONN_*` / `AIRFLOW_VAR_*` через env (Environment Variables Secret Backend).

## Граница Dev/Prod

1. `docker-compose` и `.env` в этом репозитории используются только для локальной разработки.
2. Для production секреты не должны храниться в Git, `Dockerfile` и `docker-compose*.yml`.
3. Продовый источник секретов: Vault/Cloud Secret Manager + runtime-инъекция в сервисы.

## Локальная разработка

1. Создай локальные файлы из шаблонов:
   - `cp .env.example .env`
   - `cp batch/airflow/.env.example batch/airflow/.env`
2. Заполни все `CHANGE_ME_*`.
3. Не коммить реальные значения.

## Airflow Secrets

В проекте поддержаны два способа:

1. Рекомендуемый: `AIRFLOW_CONN_SWIPEIT_BATCH_DB`  
   Пример:
   `AIRFLOW_CONN_SWIPEIT_BATCH_DB=postgresql://postgres:YOUR_PASSWORD@postgres:5432/swipeit`
2. Legacy fallback: `BATCH_DB_URL`

DAG `swipeit_daily_metrics` сначала пытается взять `BATCH_DB_URL`,  
если его нет, использует Airflow connection по `SWIPEIT_BATCH_DB_CONN_ID` (по умолчанию `swipeit_batch_db`).

## GitHub Secrets (минимальный набор)

Для CI/CD и деплоя добавь в GitHub Secrets:

1. `SECRET_KEY`
2. `DB_URL`
3. `POSTGRES_PASSWORD`
4. `MINIO_ROOT_USER`
5. `MINIO_ROOT_PASSWORD`
6. `S3_ACCESS_KEY`
7. `S3_SECRET_KEY`
8. `AIRFLOW_ADMIN_PASSWORD`
9. `AIRFLOW_CONN_SWIPEIT_BATCH_DB`

## Пример прокидывания секретов в workflow

```yaml
env:
  SECRET_KEY: ${{ secrets.SECRET_KEY }}
  DB_URL: ${{ secrets.DB_URL }}
  AIRFLOW_ADMIN_PASSWORD: ${{ secrets.AIRFLOW_ADMIN_PASSWORD }}
  AIRFLOW_CONN_SWIPEIT_BATCH_DB: ${{ secrets.AIRFLOW_CONN_SWIPEIT_BATCH_DB }}
```

## Правила безопасности

1. Не добавлять реальные пароли в `.env.example`, `README`, `docker-compose*.yml`.
2. Любой новый секрет добавлять одновременно:
   - в `.env.example` как `CHANGE_ME_*` или пустое поле,
   - в `batch/airflow/.env.example` при необходимости,
   - в GitHub Secrets (если используется в CI/CD).
3. Для Airflow UI пароль всегда задавать явно (`AIRFLOW_ADMIN_PASSWORD`), без default `admin`.
4. Секреты должны попадать в контейнер только в runtime, а не на этапе `docker build`.
