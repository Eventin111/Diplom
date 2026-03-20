# поля для таблиц sqlalchemy со временем, чтобы их не писать заново в каждой таблице

from sqlalchemy import Column, DateTime, func

class TimestampMixin:
    """Миксин для полей created_at и updated_at"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)