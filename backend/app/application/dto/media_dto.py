from enum import Enum
from typing import Optional

from pydantic import BaseModel, validator


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    MESH = "mesh"


class MediaBase(BaseModel):
    kind: MediaType
    storage_key: str


class MediaCreate(MediaBase):
    width: Optional[int] = None
    height: Optional[int] = None

    @validator("width", "height")
    def validate_dimensions(cls, value):
        if value is not None and value <= 0:
            raise ValueError("Dimensions must be positive integers")
        return value


class MediaUpdate(BaseModel):
    width: Optional[int] = None
    height: Optional[int] = None
