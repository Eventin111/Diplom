# Секреты (коротко)

## Где храним

1. Локально: `.env` и `batch/airflow/.env` (эти файлы не в git).
2. GitHub: `Settings -> Secrets and variables -> Actions`.
3. Airflow: env-переменные (`AIRFLOW_CONN_*`, `AIRFLOW_VAR_*`).

## Что сделать локально

1. `cp .env.example .env`
2. `cp batch/airflow/.env.example batch/airflow/.env`
3. Заполнить `CHANGE_ME_*` значениями.

## Airflow: секрет БД

Поддерживаются 2 варианта:

1. Основной: `AIRFLOW_CONN_SWIPEIT_BATCH_DB`
2. Fallback: `BATCH_DB_URL`

Порядок в DAG: сначала `BATCH_DB_URL`, если пусто — `AIRFLOW_CONN_*` по `SWIPEIT_BATCH_DB_CONN_ID` (обычно `swipeit_batch_db`).

## GitHub Secrets (минимум)

`SECRET_KEY`, `DB_URL`, `POSTGRES_PASSWORD`, `MINIO_ROOT_USER`, `MINIO_ROOT_PASSWORD`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`, `AIRFLOW_ADMIN_PASSWORD`, `AIRFLOW_CONN_SWIPEIT_BATCH_DB`.

## GitHub Secrets (деплой backend)

`DEPLOY_HOST`, `DEPLOY_PORT`, `DEPLOY_USER`, `DEPLOY_SSH_KEY`, `DEPLOY_PATH`, `GHCR_USERNAME`, `GHCR_READ_TOKEN`.

## Правила
1. Не писать реальные секреты в `.env.example`, `README`, `docker-compose*.yml`.
2. Новый секрет добавлять сразу в шаблон `.env.example` и в GitHub Secrets (если нужен в CI/CD).
3. `AIRFLOW_ADMIN_PASSWORD` задавать явно, не использовать `admin`.
4. Секреты передавать только в runtime, не на этапе `docker build`.
