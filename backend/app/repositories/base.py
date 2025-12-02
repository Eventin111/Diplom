from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import logging

from app.core.db import Base

logger = logging.getLogger(__name__)
ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Базовый асинхронный репозиторий с общими CRUD операциями и обработкой ошибок"""
    
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def _handle_db_error(self, operation: str, error: Exception):
        """Обработка ошибок базы данных"""
        logger.error(f"Ошибка при {operation}: {error}")
        
        if isinstance(error, IntegrityError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нарушение целостности данных (возможно, дубликат или неверная ссылка)"
            )
        elif isinstance(error, SQLAlchemyError):
            # Логируем полную ошибку для дебага
            logger.error(f"SQLAlchemy ошибка детально: {str(error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка базы данных" 
            )
        else:
            # Для всех других ошибок
            logger.exception(f"Неожиданная ошибка при {operation}:")  # Это выведет traceback
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Внутренняя ошибка сервера: {str(error)}"
            )

    async def get(self, db: AsyncSession, id: int) -> Optional[ModelType]:
        """Получить объект по ID"""
        logger.info(f"BaseRepository.get вызван для модели {self.model.__name__} с id={id}")
        try:
            result = await db.execute(select(self.model).where(self.model.id == id))
            obj = result.scalar_one_or_none()
            logger.info(f"BaseRepository.get результат: {obj}")
            return obj
        except Exception as e:
            logger.error(f"Исключение в BaseRepository.get: {e}", exc_info=True)
            # Пробрасываем исключение дальше для нормальной обработки
            raise

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        try:
            result = await db.execute(
                select(self.model).offset(skip).limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            await self._handle_db_error(f"получении списка {self.model.__name__}", e)

    async def create(self, db: AsyncSession, *, obj_in: Dict[str, Any]) -> ModelType:
        try:
            db_obj = self.model(**obj_in)
            db.add(db_obj)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except Exception as e:
            await db.rollback()
            await self._handle_db_error(f"создании {self.model.__name__}", e)

    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, obj_in: Dict[str, Any]
    ) -> ModelType:
        try:
            for field, value in obj_in.items():
                if value is not None:
                    setattr(db_obj, field, value)
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except Exception as e:
            await db.rollback()
            await self._handle_db_error(f"обновлении {self.model.__name__} с id {db_obj.id}", e)

    async def delete(self, db: AsyncSession, *, id: int) -> bool:
        try:
            result = await db.execute(
                delete(self.model).where(self.model.id == id)
            )
            await db.commit()
            return result.rowcount > 0
        except Exception as e:
            await db.rollback()
            await self._handle_db_error(f"удалении {self.model.__name__} с id {id}", e)

    async def count(self, db: AsyncSession) -> int:
        try:
            result = await db.execute(select(self.model))
            return len(result.scalars().all())
        except Exception as e:
            await self._handle_db_error(f"подсчете {self.model.__name__}", e)