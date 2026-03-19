"""
API эндпоинты для виртуальной примерки одежды (Try-On).
Presentation Layer - маршрутизация, создание сессии и сохранение результатов.
"""

import base64
import io
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.tryon_use_case import TryOnUseCase
from app.application.dto.tryon_dto import TryOnRequest
from app.core.db import get_db
from app.core.security import get_current_user
from app.infrastructure.ml.ootd_service import get_ootd_service
from app.repositories.media_repo import MediaRepository
from app.repositories.tryon_repo import TryOnRepository
from app.schemas.media import MediaType
from app.schemas.tryon import TryOnSessionCreate, TryOnStatus
from app.schemas.user import UserResponse

router = APIRouter()


def get_tryon_use_case() -> TryOnUseCase:
    """
    Dependency для получения Use Case.
    Реализует Dependency Injection.
    """
    ml_service = get_ootd_service()
    return TryOnUseCase(ml_service)


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
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    use_case: TryOnUseCase = Depends(get_tryon_use_case),
):
    """
    Запустить виртуальную примерку одежды.
    
    Параметры:
        model_image: Фото человека (JPG, PNG)
        cloth_image: Фото одежды (JPG, PNG)
        model_type: "hd" - half-body, "dc" - full-body
        category: 0=upperbody, 1=lowerbody, 2=dress
        scale: масштаб (рекомендуется 1.5-2.5)
        num_steps: шаги инференса
        num_samples: количество результатов
        seed: -1 для случайного, число для воспроизводимости
    """
    # Загрузка изображений из HTTP запроса
    model_bytes = await model_image.read()
    cloth_bytes = await cloth_image.read()

    try:
        model_img = Image.open(io.BytesIO(model_bytes))
        cloth_img = Image.open(io.BytesIO(cloth_bytes))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при чтении изображений: {str(e)}"
        )

    media_repo = MediaRepository()
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

    avatar_media_id = await persist_media(model_bytes, model_image.filename or "model.png", model_image.content_type or "image/png")
    cloth_media_id = await persist_media(cloth_bytes, cloth_image.filename or "cloth.png", cloth_image.content_type or "image/png")

    session = await tryon_repo.create(
        db,
        obj_in=TryOnSessionCreate(
            garment_id=None,
            avatar_media_id=avatar_media_id,
            cloth_media_id=cloth_media_id,
        ),
        user_id=current_user.id,
    )
    await tryon_repo.update_status(db, session.id, TryOnStatus.PROCESSING)
    
    # Создание DTO запроса
    request = TryOnRequest(
        model_image=model_img,
        cloth_image=cloth_img,
        model_type=model_type,
        category=category,
        scale=scale,
        num_steps=num_steps,
        num_samples=num_samples,
        seed=seed,
    )
    
    # Выполнение Use Case (бизнес-логика)
    try:
        result = use_case.execute(request)
        result_media_id = None
        result_urls = result.results

        if result.results:
            encoded_result = result.results[0].split(",", 1)[-1]
            result_bytes = base64.b64decode(encoded_result)
            result_media = await media_repo.create_with_upload(
                db,
                file_content=result_bytes,
                file_key=build_file_key("result", "result.png"),
                kind=MediaType.IMAGE,
                owner_user_id=current_user.id,
                content_type="image/png",
            )
            result_media_id = result_media.id

            public_url = None
            try:
                from app.core.config import settings
                public_url = f"{settings.s3_public_url}/{settings.S3_BUCKET_NAME}/{result_media.storage_key}"
            except Exception:
                public_url = None

            if public_url:
                result_urls = [public_url]

        await tryon_repo.update_status(
            db,
            session.id,
            TryOnStatus.COMPLETED,
            result_media_id=result_media_id,
        )
        return {
            "success": result.success,
            "results": result_urls,
            "count": result.count,
            "session_id": session.id,
            "result_media_id": result_media_id,
        }
    except ValueError as e:
        # Ошибки валидации
        await tryon_repo.update_status(db, session.id, TryOnStatus.FAILED, error_text=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Ошибки выполнения
        await tryon_repo.update_status(db, session.id, TryOnStatus.FAILED, error_text=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при инференсе: {str(e)}"
        )
    

@router.get("/health")
async def health_check(use_case: TryOnUseCase = Depends(get_tryon_use_case)):
    """
    Проверка готовности ML сервиса.
    """
    ml_service = use_case._ml_service
    return ml_service.health_check()
