from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.db import Base
from app.infrastructure.persistence.models.mixins import TimestampMixin


class FeedItem(Base, TimestampMixin):
    __tablename__ = "feed_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    garment_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("garments.id"), nullable=True)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", lazy="joined")
    garment = relationship("Garment", lazy="joined")
