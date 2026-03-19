from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class TryOnStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TryOnEventType(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    RETRY = "retry"
    RECOVERED = "recovered"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTERED = "dead_lettered"

class TryOnSessionBase(BaseModel):
    garment_id: Optional[int] = None
    avatar_media_id: Optional[int] = None
    cloth_media_id: Optional[int] = None

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
