from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator

from app.application.dto.media_dto import MediaBase, MediaCreate, MediaType, MediaUpdate


class MediaResponse(MediaBase):
    id: int
    owner_user_id: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    aspect_ratio: Optional[float] = None
    public_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("aspect_ratio", always=True)
    def calculate_aspect_ratio(cls, value, values):
        width = values.get("width")
        height = values.get("height")
        if width and height and height > 0:
            return round(width / height, 2)
        return None

    class Config:
        orm_mode = True


class MediaUploadResponse(BaseModel):
    media: MediaResponse
    upload_url: Optional[str] = None
