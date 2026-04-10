from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.application.dto.tryon_session_dto import TryOnSessionBase, TryOnSessionCreate, TryOnSessionUpdate
from app.domain.enums.tryon import TryOnEventType, TryOnStatus


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
