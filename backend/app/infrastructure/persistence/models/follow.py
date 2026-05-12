from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.db import Base
from app.infrastructure.persistence.models.mixins import TimestampMixin


class FollowRelation(Base, TimestampMixin):
    __tablename__ = "follow_relations"
    __table_args__ = (UniqueConstraint("follower_id", "following_id", name="uq_follow_relations_pair"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    follower_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    following_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
