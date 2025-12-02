from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class TryOnStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TryOnSessionBase(BaseModel):
    garment_id: int
    avatar_media_id: int

class TryOnSessionCreate(TryOnSessionBase):
    pass

class TryOnSessionUpdate(BaseModel):
    status: Optional[TryOnStatus] = None
    result_media_id: Optional[int] = None
    error_text: Optional[str] = None

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