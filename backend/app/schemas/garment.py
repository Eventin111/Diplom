from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any
from .media import MediaResponse

class TitleValidationMixin():
    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Название не может быть пустым')
        return v.strip()

class GarmentBase(BaseModel, TitleValidationMixin):
    title: str = Field(..., min_length=1, max_length=255, description="Название одежды")
    brand: Optional[str] = Field(None, max_length=255, description="Бренд")

class GarmentCreate(GarmentBase):
    media_id: Optional[int] = Field(None, gt=0, description="ID медиа файла")
    garment_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('media_id')
    def media_id_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('media_id должен быть положительным числом')
        return v

class GarmentUpdate(BaseModel, TitleValidationMixin):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    brand: Optional[str] = Field(None, max_length=255)
    media_id: Optional[int] = Field(None, gt=0)
    garment_metadata: Optional[Dict[str, Any]] = None

class GarmentResponse(GarmentBase):
    id: int
    media_id: Optional[int] = None
    garment_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    media: Optional[MediaResponse] = None
    
    class Config:
        orm_mode = True

class GarmentWithTryOnInfo(GarmentResponse):
    can_try_on: bool = True