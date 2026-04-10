from datetime import datetime
from typing import Any, Dict, Optional

from app.application.dto.garment_dto import GarmentBase, GarmentCreate, GarmentUpdate
from app.presentation.api.schemas.media import MediaResponse

__all__ = ["GarmentBase", "GarmentCreate", "GarmentUpdate", "GarmentResponse", "GarmentWithTryOnInfo"]


class GarmentResponse(GarmentBase):
    id: int
    media_id: Optional[int] = None
    garment_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    media: Optional[MediaResponse] = None

    class Config:
        orm_mode = True


class GarmentWithTryOnInfo(GarmentResponse):
    can_try_on: bool = True
