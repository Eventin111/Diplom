import asyncio
import importlib
import sys

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request

from app.core.errors import (
    global_exception_handler,
    http_exception_handler,
    setup_exception_handlers,
    validation_exception_handler,
)


def dummy_request():
    return Request({"type": "http", "method": "GET", "path": "/"})


def reload_config_module():
    sys.modules.pop("app.core.config", None)
    return importlib.import_module("app.core.config")


def test_validation_exception_handler_formats_response():
    exc = RequestValidationError(
        [{"loc": ("body", "email"), "msg": "field required", "type": "value_error.missing"}]
    )

    response = asyncio.run(validation_exception_handler(dummy_request(), exc))

    assert response.status_code == 422
    assert response.body
    assert b"errors" in response.body
    assert b"email" in response.body


def test_http_exception_handler_passes_status_and_detail():
    response = asyncio.run(
        http_exception_handler(dummy_request(), HTTPException(status_code=403, detail="forbidden"))
    )

    assert response.status_code == 403
    assert b"forbidden" in response.body


def test_global_exception_handler_returns_generic_500():
    response = asyncio.run(global_exception_handler(dummy_request(), RuntimeError("boom")))

    assert response.status_code == 500
    assert response.body


def test_setup_exception_handlers_registers_all_handlers():
    app = FastAPI()

    setup_exception_handlers(app)

    assert RequestValidationError in app.exception_handlers
    assert HTTPException in app.exception_handlers
    assert Exception in app.exception_handlers


def test_config_builds_async_database_url_and_public_url(monkeypatch):
    monkeypatch.setenv("DB_URL", "postgresql://user:pass@localhost:5432/swipeit")
    monkeypatch.delenv("DB_ASYNC_URL", raising=False)
    monkeypatch.setenv("S3_PUBLIC_URL", "https://cdn.example.com")
    config = reload_config_module()

    assert config.settings.async_database_url == "postgresql+asyncpg://user:pass@localhost:5432/swipeit"
    assert config.settings.s3_public_url == "https://cdn.example.com"


def test_config_prefers_explicit_async_database_url(monkeypatch):
    monkeypatch.setenv("DB_ASYNC_URL", "postgresql+asyncpg://user:pass@localhost:5432/swipeit")
    config = reload_config_module()

    assert config.settings.async_database_url == "postgresql+asyncpg://user:pass@localhost:5432/swipeit"


def test_config_exposes_project_level_sections(monkeypatch):
    monkeypatch.setenv("REACT_APP_API_BASE_URL", "http://localhost:4173")
    monkeypatch.setenv("ML_DEVICE", "cpu")
    config = reload_config_module()

    assert config.project_config.root_dir.name == "SwipeIt"
    assert config.project_config.frontend.api_base_url == "http://localhost:4173"
    assert config.project_config.ml.device == "cpu"
