"""
API эндпоинты для виртуальной примерки одежды (Try-On).
Presentation Layer: создание сессий, постановка задач в очередь и опрос статуса.
"""

import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.tryon_use_case import TryOnUseCase
from app.core.config import settings
from app.domain.enums.tryon import TryOnEventType, TryOnStatus
from app.infrastructure.auth.security import get_current_user, get_user_by_token
from app.infrastructure.cache.tryon_cache import build_tryon_cache_key, get_cached_tryon_result
from app.infrastructure.cache.tryon_rate_limit import enforce_tryon_rate_limit
from app.infrastructure.db.db import AsyncSessionLocal, get_db
from app.infrastructure.maintenance.tryon_cleanup import run_tryon_cleanup
from app.infrastructure.maintenance.tryon_recovery import run_tryon_recovery
from app.infrastructure.queue.tryon_queue import (
    build_tryon_task_payload,
    enqueue_tryon_task,
    get_tryon_dead_letters,
    get_tryon_processing_lock_count,
    get_tryon_queue_health,
    requeue_tryon_dead_letter,
)
from app.infrastructure.ml.ootd_service import get_ootd_service
from app.infrastructure.persistence.repositories.media_repo import MediaRepository
from app.infrastructure.persistence.repositories.tryon_event_repo import TryOnEventRepository
from app.infrastructure.persistence.repositories.tryon_repo import TryOnRepository
from app.application.dto.media_dto import MediaType
from app.presentation.api.schemas.tryon import TryOnResult, TryOnSessionCreate, TryOnSessionResponse
from app.presentation.api.schemas.user import UserResponse
import asyncio

router = APIRouter()


def get_tryon_use_case() -> TryOnUseCase:
    ml_service = get_ootd_service()
    return TryOnUseCase(ml_service)


def _build_media_file_url(media_id: int | None) -> str | None:
    if media_id is None:
        return None
    return f"{settings.API_V1}/media/{media_id}/file"


async def enforce_current_user_tryon_rate_limit(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    await enforce_tryon_rate_limit(current_user.id)
    return current_user


@router.post("/try-on")
async def try_on(
    model_image: UploadFile = File(..., description="Фото человека"),
    cloth_image: UploadFile = File(..., description="Фото одежды"),
    model_type: str = "hd",
    category: int = 0,
    scale: float = 2.0,
    num_steps: int = 4,
    num_samples: int = 1,
    seed: int = -1,
    current_user: UserResponse = Depends(enforce_current_user_tryon_rate_limit),
    db: AsyncSession = Depends(get_db),
    use_case: TryOnUseCase = Depends(get_tryon_use_case),
):
    model_bytes = await model_image.read()
    cloth_bytes = await cloth_image.read()

    media_repo = MediaRepository()
    event_repo = TryOnEventRepository()
    tryon_repo = TryOnRepository()

    def build_file_key(kind: str, filename: str) -> str:
        extension = os.path.splitext(filename or "")[1] or ".png"
        return f"user_{current_user.id}/tryon/{kind}/{uuid.uuid4()}{extension}"

    async def persist_media(file_bytes: bytes, file_name: str, content_type: str) -> int:
        media = await media_repo.create_with_upload(
            db,
            file_content=file_bytes,
            file_key=build_file_key("input", file_name),
            kind=MediaType.IMAGE,
            owner_user_id=current_user.id,
            content_type=content_type or "image/png",
        )
        return media.id

    try:
        use_case.validate_payload(
            model_type=model_type,
            category=category,
            scale=scale,
            num_steps=num_steps,
            num_samples=num_samples,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    avatar_media_id = await persist_media(
        model_bytes,
        model_image.filename or "model.png",
        model_image.content_type or "image/png",
    )
    cloth_media_id = await persist_media(
        cloth_bytes,
        cloth_image.filename or "cloth.png",
        cloth_image.content_type or "image/png",
    )

    session = await tryon_repo.create(
        db,
        obj_in=TryOnSessionCreate(
            garment_id=None,
            avatar_media_id=avatar_media_id,
            cloth_media_id=cloth_media_id,
        ),
        user_id=current_user.id,
    )
    await event_repo.create_event(
        db,
        session_id=session.id,
        event_type=TryOnEventType.QUEUED,
        attempt=0,
        details="Try-on session created",
    )

    cache_key = build_tryon_cache_key(
        model_bytes=model_bytes,
        cloth_bytes=cloth_bytes,
        model_type=model_type,
        category=category,
        scale=scale,
        num_steps=num_steps,
        num_samples=num_samples,
        seed=seed,
    )
    cached_result = await get_cached_tryon_result(cache_key)
    if cached_result and cached_result.get("results"):
        result_media_id = cached_result.get("result_media_id")
        await tryon_repo.update_status(
            db,
            session.id,
            TryOnStatus.COMPLETED,
            result_media_id=result_media_id,
        )
        await event_repo.create_event(
            db,
            session_id=session.id,
            event_type=TryOnEventType.COMPLETED,
            attempt=0,
            details="Served from Redis cache",
        )
        return {
            "success": True,
            "queued": False,
            "status": TryOnStatus.COMPLETED,
            "results": cached_result["results"],
            "count": len(cached_result["results"]),
            "session_id": session.id,
            "result_media_id": result_media_id,
            "cached": True,
        }

    try:
        task = build_tryon_task_payload(
            session_id=session.id,
            user_id=current_user.id,
            avatar_media_id=avatar_media_id,
            cloth_media_id=cloth_media_id,
            model_type=model_type,
            category=category,
            scale=scale,
            num_steps=num_steps,
            num_samples=num_samples,
            seed=seed,
        )
        await enqueue_tryon_task(task)
    except Exception as exc:
        await tryon_repo.update_status(db, session.id, TryOnStatus.FAILED, error_text=str(exc))
        await event_repo.create_event(
            db,
            session_id=session.id,
            event_type=TryOnEventType.FAILED,
            attempt=0,
            error_text=str(exc),
            details="Failed to enqueue try-on task",
        )
        raise HTTPException(status_code=500, detail=f"Ошибка постановки задачи в очередь: {str(exc)}")

    return {
        "success": True,
        "queued": True,
        "status": TryOnStatus.QUEUED,
        "results": [],
        "count": 0,
        "session_id": session.id,
        "result_media_id": None,
        "cached": False,
    }


@router.get("/sessions/{session_id}", response_model=TryOnResult)
async def get_tryon_session(
    session_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tryon_repo = TryOnRepository()
    tryon_event_repo = TryOnEventRepository()
    session = await tryon_repo.get(db, session_id)

    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Try-on session not found")

    return TryOnResult(
        session=TryOnSessionResponse.from_orm(session),
        result_image_url=_build_media_file_url(session.result_media_id),
    )


@router.websocket("/sessions/{session_id}/ws")
async def tryon_session_websocket(websocket: WebSocket, session_id: int):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
        return

    await websocket.accept()

    try:
        async with AsyncSessionLocal() as db:
            current_user = await get_user_by_token(token=token, db=db)
            tryon_repo = TryOnRepository()
            last_payload = None

            while True:
                session = await tryon_repo.get(db, session_id)
                if session is None or session.user_id != current_user.id:
                    await websocket.send_json({"error": "Try-on session not found"})
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return

                payload = {
                    "session_id": session.id,
                    "status": session.status,
                    "result_media_id": session.result_media_id,
                    "result_image_url": _build_media_file_url(session.result_media_id),
                    "error_text": session.error_text,
                }
                if payload != last_payload:
                    await websocket.send_json(payload)
                    last_payload = payload

                if session.status in {TryOnStatus.COMPLETED, TryOnStatus.FAILED}:
                    await websocket.close()
                    return

                await asyncio.sleep(1)
                await db.refresh(session)
    except HTTPException:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Unauthorized")
    except WebSocketDisconnect:
        return


@router.get("/health")
async def health_check(use_case: TryOnUseCase = Depends(get_tryon_use_case)):
    ml_service = use_case._ml_service
    return ml_service.health_check()


@router.get("/queue/health")
async def queue_health_check():
    try:
        return await get_tryon_queue_health()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Try-on queue unavailable: {str(exc)}")


@router.get("/queue/dead-letter")
async def tryon_dead_letter_queue(
    limit: int = 20,
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        return {
            "dead_letters": await get_tryon_dead_letters(limit=limit),
            "requested_by_user_id": current_user.id,
        }
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Try-on dead-letter queue unavailable: {str(exc)}")


@router.post("/queue/dead-letter/{index}/requeue")
async def requeue_dead_letter_tryon(
    index: int,
    current_user: UserResponse = Depends(get_current_user),
):
    try:
        payload = await requeue_tryon_dead_letter(index)
        payload["requested_by_user_id"] = current_user.id
        return payload
    except IndexError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Try-on dead-letter requeue unavailable: {str(exc)}")


@router.get("/system/metrics")
async def tryon_system_metrics(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tryon_repo = TryOnRepository()

    try:
        queue_health = await get_tryon_queue_health()
        processing_locks = await get_tryon_processing_lock_count()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Try-on metrics unavailable: {str(exc)}")

    return {
        "queue": {
            **queue_health,
            "processing_locks": processing_locks,
        },
        "sessions": {
            "status_counts": await tryon_repo.get_status_counts(db),
            "recent_failures": await tryon_repo.get_recent_failures(db, limit=5),
            "recent_events": await tryon_event_repo.get_recent_events(db, limit=10),
        },
        "requested_by_user_id": current_user.id,
    }


@router.post("/recovery/stale")
async def recover_stale_tryon_sessions(
    current_user: UserResponse = Depends(get_current_user),
):
    payload = await run_tryon_recovery(force=True)
    payload["requested_by_user_id"] = current_user.id
    return payload


@router.post("/cleanup/run")
async def run_tryon_cleanup_now(
    current_user: UserResponse = Depends(get_current_user),
):
    payload = await run_tryon_cleanup(force=True)
    payload["requested_by_user_id"] = current_user.id
    payload["retention_days"] = settings.TRYON_RETENTION_DAYS
    return payload
