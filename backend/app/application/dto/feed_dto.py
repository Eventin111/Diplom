from typing import List, Optional

from pydantic import BaseModel, Field, validator


class FeedItemBase(BaseModel):
    caption: Optional[str] = Field(None, max_length=2000)


class FeedItemCreate(FeedItemBase):
    garment_id: Optional[int] = Field(None, gt=0)
    media_ids: List[int] = Field(default_factory=list)

    @validator("garment_id")
    def garment_id_positive(cls, value):
        if value is not None and value <= 0:
            raise ValueError("garment_id must be a positive integer")
        return value

    @validator("media_ids", each_item=True)
    def media_ids_positive(cls, value):
        if value <= 0:
            raise ValueError("media_ids must contain positive integers")
        return value


class FeedItemUpdate(BaseModel):
    caption: Optional[str] = Field(None, max_length=2000)
