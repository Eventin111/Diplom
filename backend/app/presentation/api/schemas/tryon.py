from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.application.dto.tryon_session_dto import TryOnSessionBase, TryOnSessionCreate, TryOnSessionUpdate
from app.domain.enums.tryon import TryOnEventType, TryOnStatus

__all__ = [
    "TryOnSessionBase",
    "TryOnSessionCreate",
    "TryOnSessionUpdate",
    "TryOnSessionResponse",
    "TryOnResult",
    "TryOnEventResponse",
    "RecentTryOnItem",
    "RecentTryOnList",
    "PublishTryOnRequest",
    "PublishTryOnResponse",
]


class TryOnSessionResponse(TryOnSessionBase):
    id: int
    user_id: int
    status: TryOnStatus
    result_media_id: Optional[int] = None
    error_text: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class TryOnResult(BaseModel):
    session: TryOnSessionResponse
    result_image_url: Optional[str] = None


class TryOnEventResponse(BaseModel):
    id: int
    session_id: int
    event_type: TryOnEventType
    attempt: Optional[int] = None
    error_text: Optional[str] = None
    details: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True


class RecentTryOnItem(BaseModel):
    session_id: int
    status: TryOnStatus
    created_at: datetime
    avatar_image_url: Optional[str] = None
    cloth_image_url: Optional[str] = None
    result_image_url: Optional[str] = None
    error_text: Optional[str] = None
    published_post_id: Optional[int] = None


class RecentTryOnList(BaseModel):
    items: list[RecentTryOnItem]


class PublishTryOnRequest(BaseModel):
    caption: Optional[str] = None
    source_type: Optional[str] = None
    source_post_id: Optional[int] = None
    hashtags: list[str] = Field(default_factory=list)


class PublishTryOnResponse(BaseModel):
    feed_item_id: int
    garment_id: int
    image_url: Optional[str] = None
