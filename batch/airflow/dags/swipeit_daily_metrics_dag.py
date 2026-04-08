from __future__ import annotations

import os
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.hooks.base import BaseHook
from airflow.providers.docker.operators.docker import DockerOperator


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


DEFAULT_BATCH_IMAGE = os.getenv("SWIPEIT_BATCH_IMAGE", "swipeit-batch:latest")
DEFAULT_DOCKER_NETWORK = os.getenv("SWIPEIT_DOCKER_NETWORK", "diplom_default")
DEFAULT_BATCH_DB_CONN_ID = os.getenv("SWIPEIT_BATCH_DB_CONN_ID", "swipeit_batch_db")
DEFAULT_INTERRUPTED_STATUSES = os.getenv("TRYON_INTERRUPTED_STATUSES", "failed")
DEFAULT_SCHEDULE = os.getenv("SWIPEIT_DAG_SCHEDULE", "0 2 * * *")
DEFAULT_TASK_TIMEOUT_MINUTES = _env_int("SWIPEIT_TASK_TIMEOUT_MINUTES", 30)
DEFAULT_DAGRUN_TIMEOUT_MINUTES = _env_int("SWIPEIT_DAGRUN_TIMEOUT_MINUTES", 60)
DEFAULT_RETRIES = _env_int("SWIPEIT_DAG_RETRIES", 2)
DEFAULT_RETRY_DELAY_MINUTES = _env_int("SWIPEIT_DAG_RETRY_DELAY_MINUTES", 5)
DEFAULT_MAX_ACTIVE_RUNS = _env_int("SWIPEIT_MAX_ACTIVE_RUNS", 1)
DEFAULT_MAX_ACTIVE_TASKS = _env_int("SWIPEIT_MAX_ACTIVE_TASKS", 2)
DEFAULT_CATCHUP = _env_bool("SWIPEIT_DAG_CATCHUP", True)


def _resolve_batch_db_url() -> str:
    direct_url = os.getenv("BATCH_DB_URL")
    if direct_url:
        return direct_url

    try:
        conn = BaseHook.get_connection(DEFAULT_BATCH_DB_CONN_ID)
    except Exception as exc:
        raise RuntimeError(
            "Batch DB secret is missing. Set BATCH_DB_URL or AIRFLOW_CONN_"
            f"{DEFAULT_BATCH_DB_CONN_ID.upper()}."
        ) from exc

    conn_uri = conn.get_uri()
    if not conn_uri:
        raise RuntimeError(
            f"Airflow connection '{DEFAULT_BATCH_DB_CONN_ID}' is empty. "
            "Set BATCH_DB_URL or AIRFLOW_CONN value."
        )

    return conn_uri


DEFAULT_BATCH_DB_URL = _resolve_batch_db_url()


with DAG(
    dag_id="swipeit_daily_metrics",
    description="Daily batch metrics for users/feed/likes/try-on",
    schedule=DEFAULT_SCHEDULE,
    start_date=pendulum.datetime(2026, 4, 1, tz="UTC"),
    catchup=DEFAULT_CATCHUP,
    max_active_runs=DEFAULT_MAX_ACTIVE_RUNS,
    max_active_tasks=DEFAULT_MAX_ACTIVE_TASKS,
    dagrun_timeout=timedelta(minutes=DEFAULT_DAGRUN_TIMEOUT_MINUTES),
    default_args={
        "owner": "swipeit",
        "depends_on_past": False,
        "retries": DEFAULT_RETRIES,
        "retry_delay": timedelta(minutes=DEFAULT_RETRY_DELAY_MINUTES),
        "retry_exponential_backoff": True,
    },
    tags=["swipeit", "batch", "metrics"],
) as dag:
    build_daily_metrics = DockerOperator(
        task_id="build_daily_metrics",
        image=DEFAULT_BATCH_IMAGE,
        command="--run-date {{ ds }} --mode aggregate",
        docker_url="unix://var/run/docker.sock",
        network_mode=DEFAULT_DOCKER_NETWORK,
        environment={
            "BATCH_DB_URL": DEFAULT_BATCH_DB_URL,
            "TRYON_INTERRUPTED_STATUSES": DEFAULT_INTERRUPTED_STATUSES,
        },
        execution_timeout=timedelta(minutes=DEFAULT_TASK_TIMEOUT_MINUTES),
        auto_remove="success",
        mount_tmp_dir=False,
        tty=False,
    )

    validate_daily_metrics = DockerOperator(
        task_id="validate_daily_metrics",
        image=DEFAULT_BATCH_IMAGE,
        command="--run-date {{ ds }} --mode validate",
        docker_url="unix://var/run/docker.sock",
        network_mode=DEFAULT_DOCKER_NETWORK,
        environment={
            "BATCH_DB_URL": DEFAULT_BATCH_DB_URL,
            "TRYON_INTERRUPTED_STATUSES": DEFAULT_INTERRUPTED_STATUSES,
        },
        execution_timeout=timedelta(minutes=DEFAULT_TASK_TIMEOUT_MINUTES),
        auto_remove="success",
        mount_tmp_dir=False,
        tty=False,
    )

    build_daily_metrics >> validate_daily_metrics
