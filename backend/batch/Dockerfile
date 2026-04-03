FROM python:3.10-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir "SQLAlchemy[asyncio]==2.0.23" asyncpg==0.29.0

COPY swipeit_daily_metrics_job.py /app/swipeit_daily_metrics_job.py

ENTRYPOINT ["python", "/app/swipeit_daily_metrics_job.py"]
