import io
from PIL import Image
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    @staticmethod
    def get_image_dimensions(image_data: bytes) -> Optional[Tuple[int, int]]:
        """Получить ширину и высоту изображения из байтов"""
        try:
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            logger.info(f"Изображение размером: {width}x{height}")
            return width, height
        except Exception as e:
            logger.error(f"Ошибка при получении размеров изображения: {e}")
            return None
    
    @staticmethod
    def is_image_vertical(width: int, height: int, threshold: float = 1.2) -> bool:
        """Определяет, является ли изображение вертикальным (для мобильных устройств)"""
        return height > width * threshold
    
    @staticmethod
    def get_image_format(image_data: bytes) -> Optional[str]:
        """Определить формат изображения"""
        try:
            image = Image.open(io.BytesIO(image_data))
            return image.format
        except Exception as e:
            logger.error(f"Ошибка при определении формата изображения: {e}")
            return None