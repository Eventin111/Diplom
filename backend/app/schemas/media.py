from pydantic import BaseModel, AnyUrl, validator
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
    width: Optional[int] = None
    height: Optional[int] = None
    
    @validator('width', 'height')
    def validate_dimensions(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Размеры должны быть положительными числами')
        return v

class MediaUpdate(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None

class MediaResponse(MediaBase):
    id: int
    owner_user_id: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[float] = None  # Добавляем соотношение сторон
    public_url: Optional[AnyUrl] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @validator('aspect_ratio', always=True)
    def calculate_aspect_ratio(cls, v, values):
        """Вычисляем соотношение сторон из width и height"""
        width = values.get('width')
        height = values.get('height')
        
        if width and height and height > 0:
            return round(width / height, 2)
        return None
    
    class Config:
        orm_mode = True

class MediaUploadResponse(BaseModel):
    """Ответ после загрузки медиа"""
    media: MediaResponse
    upload_url: Optional[str] = None