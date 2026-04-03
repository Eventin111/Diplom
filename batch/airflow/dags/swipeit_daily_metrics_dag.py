from __future__ import annotations

import os
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator


DEFAULT_BATCH_IMAGE = os.getenv("SWIPEIT_BATCH_IMAGE", os.getenv("TRYON_BATCH_IMAGE", "swipeit-batch:latest"))
DEFAULT_DOCKER_NETWORK = os.getenv(
    "SWIPEIT_DOCKER_NETWORK",
    os.getenv("TRYON_DOCKER_NETWORK", "diplom_default"),
)
DEFAULT_BATCH_DB_URL = os.getenv(
    "BATCH_DB_URL",
    "postgresql://postgres:swipeit-gon-make-it@postgres:5432/swipeit",
)


with DAG(
    dag_id="swipeit_daily_metrics",
    description="Daily batch metrics for users/feed/likes/try-on",
    schedule="0 2 * * *",
    start_date=pendulum.datetime(2026, 4, 1, tz="UTC"),
    catchup=True,
    max_active_runs=1,
    default_args={
        "owner": "swipeit",
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    tags=["swipeit", "batch", "metrics"],
) as dag:
    build_daily_metrics = DockerOperator(
        task_id="build_daily_metrics",
        image=DEFAULT_BATCH_IMAGE,
        command="--run-date {{ ds }} --mode aggregate",
        docker_url="unix://var/run/docker.sock",
        network_mode=DEFAULT_DOCKER_NETWORK,
        environment={"BATCH_DB_URL": DEFAULT_BATCH_DB_URL},
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
        environment={"BATCH_DB_URL": DEFAULT_BATCH_DB_URL},
        auto_remove="success",
        mount_tmp_dir=False,
        tty=False,
    )

    build_daily_metrics >> validate_daily_metrics
