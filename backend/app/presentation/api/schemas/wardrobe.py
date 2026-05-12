from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.application.dto.wardrobe_dto import WardrobeItemCreate, WardrobeSaveFromPost

__all__ = [
    "WardrobeItemCreate",
    "WardrobeSaveFromPost",
    "WardrobeItemResponse",
    "WardrobeGarmentResponse",
    "WardrobeListResponse",
]


class WardrobeGarmentResponse(BaseModel):
    id: int
    title: str
    brand: Optional[str] = None
    media_id: Optional[int] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    price: Optional[str] = None
    source_post_id: Optional[int] = None
    created_at: datetime


class WardrobeItemResponse(BaseModel):
    id: int
    user_id: int
    garment_id: int
    created_at: datetime
    garment: WardrobeGarmentResponse

    class Config:
        orm_mode = True


class WardrobeListResponse(BaseModel):
    items: list[WardrobeItemResponse]
