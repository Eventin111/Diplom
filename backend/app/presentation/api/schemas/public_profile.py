from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PublicPostItem(BaseModel):
    feed_item_id: int
    caption: Optional[str] = None
    image_url: Optional[str] = None
    likes_count: int = 0
    comments_count: int = 0
    created_at: datetime
    source_post_id: Optional[int] = None
    source_type: Optional[str] = None
    hashtags: list[str] = Field(default_factory=list)


class PublicProfileResponse(BaseModel):
    user_id: int
    username: str
    avatar_url: Optional[str] = None
    status: Optional[str] = None
    posts_count: int = 0
    likes_count: int = 0
    wardrobe_count: int = 0
    followers_count: int = 0
    following_count: int = 0
    is_following: bool = False
    posts: list[PublicPostItem]


class PublicRelationUserItem(BaseModel):
    user_id: int
    username: str
    avatar_url: Optional[str] = None
    is_following: bool = False


class PublicRelationListResponse(BaseModel):
    items: list[PublicRelationUserItem] = Field(default_factory=list)
    total: int = 0
