from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, validator


class TitleValidationMixin:
    @validator("title", check_fields=False)
    def title_not_empty(cls, value):
        if not value or not value.strip():
            raise ValueError("Title cannot be empty")
        return value.strip()


class GarmentBase(TitleValidationMixin, BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Garment title")
    brand: Optional[str] = Field(None, max_length=255, description="Brand")

    class Config:
        anystr_strip_whitespace = True


class GarmentCreate(GarmentBase):
    media_id: Optional[int] = Field(None, gt=0, description="Media asset ID")
    garment_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator("media_id")
    def media_id_positive(cls, value):
        if value is not None and value <= 0:
            raise ValueError("media_id must be a positive integer")
        return value


class GarmentUpdate(TitleValidationMixin, BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    brand: Optional[str] = Field(None, max_length=255)
    media_id: Optional[int] = Field(None, gt=0)
    garment_metadata: Optional[Dict[str, Any]] = None

    class Config:
        anystr_strip_whitespace = True
