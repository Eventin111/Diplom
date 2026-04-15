from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.health import (
    build_backend_liveness_payload,
    build_backend_readiness_payload,
    build_tryon_queue_health_payload,
    build_tryon_service_health_payload,
    build_tryon_worker_health_payload,
)

router = APIRouter()


@router.get("/live")
async def backend_liveness():
    return build_backend_liveness_payload()


@router.get("/ready")
async def backend_readiness():
    payload = await build_backend_readiness_payload()
    status_code = 200 if payload["status"] == "ok" else 503
    return JSONResponse(status_code=status_code, content=payload)


@router.get("/tryon")
async def tryon_health():
    payload = await build_tryon_service_health_payload()
    status_code = 200 if payload["status"] == "ok" else 503
    return JSONResponse(status_code=status_code, content=payload)


@router.get("/tryon/worker")
async def tryon_worker_health():
    payload = await build_tryon_worker_health_payload()
    status_code = 200 if payload["status"] == "ok" else 503
    return JSONResponse(status_code=status_code, content=payload)


@router.get("/tryon/queue")
async def tryon_queue_health():
    payload = await build_tryon_queue_health_payload()
    status_code = 200 if payload["status"] == "ok" else 503
    return JSONResponse(status_code=status_code, content=payload)
