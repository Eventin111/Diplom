from typing import Optional

from pydantic import BaseModel

from app.domain.enums.tryon import TryOnStatus


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
