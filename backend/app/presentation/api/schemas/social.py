from datetime import datetime

from pydantic import BaseModel

from app.application.dto.social_dto import LikeBase, LikeCreate

__all__ = ["LikeBase", "LikeCreate", "LikeResponse", "LikeStats"]


class LikeResponse(LikeBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True


class LikeStats(BaseModel):
    feed_item_id: int
    likes_count: int
    is_liked: bool
