import importlib.util
import sys
from pathlib import Path


JOB_PATH = Path(__file__).resolve().parents[1] / "batch" / "swipeit_daily_metrics_job.py"


def _load_job_module():
    module_name = "swipeit_daily_metrics_job"
    spec = importlib.util.spec_from_file_location(module_name, JOB_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_to_async_db_url_accepts_postgresql_uri():
    module = _load_job_module()

    assert (
        module._to_async_db_url("postgresql://user:pass@postgres:5432/swipeit")
        == "postgresql+asyncpg://user:pass@postgres:5432/swipeit"
    )


def test_to_async_db_url_accepts_airflow_postgres_uri():
    module = _load_job_module()

    assert (
        module._to_async_db_url("postgres://user:pass@postgres:5432/swipeit")
        == "postgresql+asyncpg://user:pass@postgres:5432/swipeit"
    )
