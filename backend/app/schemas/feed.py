from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
from .user import UserResponse
from .garment import GarmentResponse
from .media import MediaResponse

class FeedItemBase(BaseModel):
    caption: Optional[str] = Field(None, max_length=2000)

class FeedItemCreate(FeedItemBase):
    garment_id: Optional[int] = Field(None, gt=0)
    media_ids: List[int] = Field(default_factory=list)

    @validator('garment_id')
    def garment_id_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('garment_id должен быть положительным числом')
        return v

    @validator('media_ids', each_item=True)
    def media_ids_positive(cls, v):
        if v <= 0:
            raise ValueError('media_ids должны быть положительными числами')
        return v

class FeedItemUpdate(BaseModel):
    caption: Optional[str] = Field(None, max_length=2000)

class FeedItemResponse(FeedItemBase):
    id: int
    user_id: int
    garment_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Вложенные объекты
    user: Optional[UserResponse] = None
    garment: Optional[GarmentResponse] = None
    media_items: List[MediaResponse] = []
    
    class Config:
        orm_mode = True

class FeedItemWithStats(FeedItemResponse):
    likes_count: int = 0
    comments_count: int = 0
    is_liked: bool = False

class FeedPagination(BaseModel):
    items: List[FeedItemWithStats]
    next_cursor: Optional[str] = None
    has_more: bool = False