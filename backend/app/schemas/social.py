from pydantic import BaseModel
from datetime import datetime

class LikeBase(BaseModel):
    feed_item_id: int

class LikeCreate(LikeBase):
    pass

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