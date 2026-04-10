from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.application.dto.feed_dto import FeedItemBase, FeedItemCreate, FeedItemUpdate
from app.presentation.api.schemas.garment import GarmentResponse
from app.presentation.api.schemas.media import MediaResponse
from app.presentation.api.schemas.user import UserResponse

__all__ = [
    "FeedItemBase",
    "FeedItemCreate",
    "FeedItemUpdate",
    "FeedItemResponse",
    "FeedItemWithStats",
    "FeedPagination",
]


class FeedItemResponse(FeedItemBase):
    id: int
    user_id: int
    garment_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
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
