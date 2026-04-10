from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.db import Base
from app.infrastructure.persistence.models.mixins import TimestampMixin


class TryOnSession(Base, TimestampMixin):
    __tablename__ = "tryon_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    avatar_media_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("media_assets.id"), nullable=True)
    cloth_media_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("media_assets.id"), nullable=True)
    garment_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("garments.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="queued")  # queued/processing/done/failed
    result_media_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("media_assets.id"), nullable=True)
    error_text: Mapped[str | None] = mapped_column(String(1024), nullable=True)
