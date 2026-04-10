from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.db import Base
from app.infrastructure.persistence.models.mixins import TimestampMixin


class Garment(Base, TimestampMixin):
    __tablename__ = "garments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    brand: Mapped[str | None] = mapped_column(String(255))
    media_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("media_assets.id"), nullable=True)

    # Переименовываем metadata в garment_metadata чтобы избежать конфликта с SQLAlchemy
    garment_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    media = relationship("MediaAsset", lazy="joined")
