"""
OOTDiffusion Service - обёртка для виртуальной примерки одежды.
Используется как библиотека для интеграции с FastAPI бэкендом.
"""

import sys
from pathlib import Path
from typing import Optional

from PIL import Image

# Добавляем путь к OOTDiffusion в sys.path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from run.ootd_app.adapters import DiffusionAdapter, OpenPoseAdapter, ParsingAdapter
from run.ootd_app.entities import InferenceRequest, InferenceResult
from run.ootd_app.usecases import RunOOTDInference


class OOTDService:
    """
    Сервис для виртуальной примерки одежды на основе OOTDiffusion.
    
    Поддерживает:
    - Half-body (верхняя часть тела) - model_type="hd"
    - Full-body (полное тело) - model_type="dc"
    
    Категории одежды (для full-body):
    - 0: upperbody (верх)
    - 1: lowerbody (низ)
    - 2: dress (платье)
    """
    
    def __init__(self, gpu_id: int = 0):
        """
        Инициализация сервиса.
        
        Args:
            gpu_id: ID GPU для инференса (по умолчанию 0)
        """
        self.gpu_id = gpu_id
        self._openpose: Optional[OpenPoseAdapter] = None
        self._parsing: Optional[ParsingAdapter] = None
        self._diffusion: Optional[DiffusionAdapter] = None
        self._runner: Optional[RunOOTDInference] = None
        
    def _ensure_initialized(self):
        """Ленивая инициализация компонентов модели."""
        if self._runner is None:
            self._openpose = OpenPoseAdapter(self.gpu_id)
            self._parsing = ParsingAdapter(self.gpu_id)
            self._diffusion = DiffusionAdapter(self.gpu_id, "hd")  # default
            self._runner = RunOOTDInference(self._openpose, self._parsing, self._diffusion)
    
    def try_on(
        self,
        model_image: Image.Image,
        cloth_image: Image.Image,
        model_type: str = "hd",
        category: int = 0,
        scale: float = 2.0,
        num_steps: int = 20,
        num_samples: int = 1,
        seed: int = -1,
    ) -> list[Image.Image]:
        """
        Запускает виртуальную примерку.
        
        Args:
            model_image: PIL Image с фото человека
            cloth_image: PIL Image с фото одежды
            model_type: "hd" (half-body) или "dc" (full-body)
            category: категория одежды (0=upperbody, 1=lowerbody, 2=dress)
            scale: масштаб изображения
            num_steps: количество шагов инференса
            num_samples: количество сэмплов для генерации
            seed: seed для воспроизводимости (-1 = случайный)
            
        Returns:
            List[PIL.Image] - список сгенерированных изображений
        """
        self._ensure_initialized()
        
        # Сохраняем временные изображения
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = Path(tmpdir) / "model.jpg"
            cloth_path = Path(tmpdir) / "cloth.jpg"
            
            model_image.save(model_path)
            cloth_image.save(cloth_path)
            
            category_dict = ["upperbody", "lowerbody", "dress"]
            
            if model_type == "hd" and category != 0:
                raise ValueError("model_type 'hd' requires category == 0 (upperbody)!")
            
            request = InferenceRequest(
                gpu_id=self.gpu_id,
                model_type=model_type,
                category=category_dict[category],
                cloth_path=str(cloth_path),
                model_path=str(model_path),
                image_scale=scale,
                num_steps=num_steps,
                num_samples=num_samples,
                seed=seed,
            )
            
            result = self._runner.execute(request)
            return result.outputs


# Глобальный экземпляр сервиса (singleton)
_service: Optional[OOTDService] = None


def get_ootd_service(gpu_id: int = 0) -> OOTDService:
    """Получить экземпляр OOTD сервиса."""
    global _service
    if _service is None:
        _service = OOTDService(gpu_id)
    return _service
