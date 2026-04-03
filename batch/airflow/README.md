# Airflow DAG для batch-аналитики SwipeIt

## Что делает DAG

`swipeit_daily_metrics` запускается ежедневно и пишет агрегаты за сутки в таблицу `daily_project_metrics`:

- `users_registered_count` из `users`
- `feed_items_created_count` из `feed_items`
- `likes_created_count` из `likes`
- `tryon_total_count` из `tryon_sessions`
- `tryon_successful_count` (статус `completed`)
- `tryon_interrupted_count` (статус `failed`)

## Шаги DAG

1. `build_daily_metrics` (`DockerOperator`)  
   Считает метрики за `{{ ds }}` и делает `UPSERT`.
2. `validate_daily_metrics` (`DockerOperator`)  
   Проверяет, что запись за `{{ ds }}` существует в `daily_project_metrics`.

## Идемпотентность

В `daily_project_metrics` ключ `metric_date` является `PRIMARY KEY`, а batch job пишет через `UPSERT`:

- повторный запуск за тот же день не создаёт дублей
- данные за день пересчитываются и обновляются

## Локальный запуск Airflow

1. Собери batch image с тегом `swipeit-batch:latest`:

```bash
docker build -t swipeit-batch:latest backend/batch
```

2. Запусти Airflow:

```bash
docker compose -f batch/airflow/docker-compose.airflow.yml up -d
```

3. Открой UI:

- URL: `http://localhost:8080`
- логин: `admin`
- пароль: `admin`

4. Включи DAG `swipeit_daily_metrics`.

## Backfill (демонстрация)

Пример бэкфилла за диапазон дат:

```bash
docker compose -f batch/airflow/docker-compose.airflow.yml exec airflow-scheduler \
  airflow dags backfill swipeit_daily_metrics \
  --start-date 2026-04-01 \
  --end-date 2026-04-07
```

Проверка результата в PostgreSQL:

```sql
SELECT *
FROM daily_project_metrics
ORDER BY metric_date DESC;
```

## Отладка job без Airflow

```bash
python backend/batch/swipeit_daily_metrics_job.py --run-date 2026-04-03 --mode aggregate
python backend/batch/swipeit_daily_metrics_job.py --run-date 2026-04-03 --mode validate
```
