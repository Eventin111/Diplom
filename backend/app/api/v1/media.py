from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import os
import logging

from app.core.db import get_db
from app.core.security import get_current_user
from app.repositories.media_repo import MediaRepository
from app.schemas.media import MediaResponse, MediaCreate, MediaType, MediaUploadResponse
from app.schemas.user import UserResponse

router = APIRouter()
logger = logging.getLogger(__name__)

# Разрешенные MIME types
ALLOWED_CONTENT_TYPES = {
    "image/jpeg": MediaType.IMAGE,
    "image/png": MediaType.IMAGE,
    "image/gif": MediaType.IMAGE,
    "image/webp": MediaType.IMAGE,
}

@router.post("/upload", response_model=MediaUploadResponse)
async def upload_media(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Загрузка медиа файла (работает с S3 и без S3)"""
    
    # Проверяем тип файла
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неподдерживаемый тип файла. Разрешены: {', '.join(ALLOWED_CONTENT_TYPES.keys())}"
        )
    
    # Генерируем уникальное имя файла
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"user_{current_user.id}/{uuid.uuid4()}{file_extension}"
    
    # Читаем содержимое файла
    file_content = await file.read()
    
    # Определяем тип медиа
    media_type = ALLOWED_CONTENT_TYPES[file.content_type]
    
    # Создаем медиа запись
    media_repo = MediaRepository()
    try:
        # Пытаемся загрузить в S3, если доступен
        media = await media_repo.create_with_upload(
            db,
            file_content=file_content,
            file_key=unique_filename,
            kind=media_type,
            owner_user_id=current_user.id,
            content_type=file.content_type
        )
        
        # Формируем URL для ответа
        from app.core.config import settings
        upload_url = None
        if hasattr(settings, 'S3_PUBLIC_URL') and settings.S3_PUBLIC_URL:
            upload_url = f"{settings.S3_PUBLIC_URL}/{settings.S3_BUCKET_NAME}/{unique_filename}"
        elif hasattr(settings, 'S3_ENDPOINT') and settings.S3_ENDPOINT:
            upload_url = f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET_NAME}/{unique_filename}"
        
        logger.info(f"Файл загружен: {unique_filename}")
        
        return MediaUploadResponse(
            media=media,
            upload_url=upload_url
        )
        
    except Exception as e:
        logger.error(f"Ошибка загрузки файла: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка загрузки файла: {str(e)}"
        )

@router.get("/{media_id}", response_model=MediaResponse)
async def get_media(
    media_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить информацию о медиа"""
    media_repo = MediaRepository()
    media = await media_repo.get(db, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Медиа не найдено")
    
    # Добавляем публичный URL если S3 настроен
    try:
        from app.core.config import settings
        if settings.S3_PUBLIC_URL:
            media.public_url = f"{settings.S3_PUBLIC_URL}/{settings.S3_BUCKET_NAME}/{media.storage_key}"
        elif settings.S3_ENDPOINT:
            media.public_url = f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET_NAME}/{media.storage_key}"
    except Exception as e:
        logger.warning(f"Не удалось добавить public_url: {e}")
    
    return media