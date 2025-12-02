from pydantic import BaseModel, AnyUrl  # Изменяем HttpUrl на AnyUrl
from datetime import datetime
from typing import Optional
from enum import Enum

class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    MESH = "mesh"

class MediaBase(BaseModel):
    kind: MediaType
    storage_key: str

class MediaCreate(MediaBase):
    pass

class MediaUpdate(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None

class MediaResponse(MediaBase):
    id: int
    owner_user_id: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    public_url: Optional[AnyUrl] = None  # Изменяем HttpUrl на AnyUrl
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class MediaUploadResponse(BaseModel):
    """Ответ после загрузки медиа"""
    media: MediaResponse
    upload_url: Optional[str] = None