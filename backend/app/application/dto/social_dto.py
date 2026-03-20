from pydantic import BaseModel


class LikeBase(BaseModel):
    feed_item_id: int


class LikeCreate(LikeBase):
    pass
