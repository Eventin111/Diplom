from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.db import Base
from app.infrastructure.persistence.models.mixins import TimestampMixin


class Like(Base, TimestampMixin):
    __tablename__ = "likes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    feed_item_id: Mapped[int] = mapped_column(Integer, ForeignKey("feed_items.id"), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("user_id", "feed_item_id", name="uq_like_user_feed"),)
