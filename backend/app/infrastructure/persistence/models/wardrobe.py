from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.db import Base
from app.infrastructure.persistence.models.mixins import TimestampMixin


class WardrobeItem(Base, TimestampMixin):
    __tablename__ = "wardrobe_items"
    __table_args__ = (UniqueConstraint("user_id", "garment_id", name="uq_wardrobe_items_user_garment"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    garment_id: Mapped[int] = mapped_column(Integer, ForeignKey("garments.id"), nullable=False, index=True)

    garment = relationship("Garment", lazy="joined")
