from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.db import Base
from app.infrastructure.persistence.models.mixins import TimestampMixin


class CommentLike(Base, TimestampMixin):
    __tablename__ = "comment_likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    comment_id: Mapped[int] = mapped_column(Integer, ForeignKey("comments.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    __table_args__ = (UniqueConstraint("comment_id", "user_id", name="uq_comment_like_user"),)
