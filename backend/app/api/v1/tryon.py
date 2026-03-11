"""
API эндпоинты для виртуальной примерки одежды (Try-On).
Presentation Layer - только маршрутизация и преобразование HTTP.

Clean Architecture:
- API (этот файл) -> Presentation Layer
- Use Case -> Application Layer
- ML Service -> Infrastructure Layer
"""

import io

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image

from app.application.use_cases.tryon_use_case import TryOnUseCase
from app.application.dto.tryon_dto import TryOnRequest
from app.infrastructure.ml.ootd_service import get_ootd_service

router = APIRouter()


def get_tryon_use_case() -> TryOnUseCase:
    """
    Dependency для получения Use Case.
    Реализует Dependency Injection.
    """
    ml_service = get_ootd_service()
    return TryOnUseCase(ml_service)


@router.post("/try-on")
async def try_on(
    model_image: UploadFile = File(..., description="Фото человека"),
    cloth_image: UploadFile = File(..., description="Фото одежды"),
    model_type: str = "hd",
    category: int = 0,
    scale: float = 2.0,
    num_steps: int = 20,
    num_samples: int = 1,
    seed: int = -1,
    use_case: TryOnUseCase = Depends(get_tryon_use_case),
):
    """
    Запустить виртуальную примерку одежды.
    
    Параметры:
        model_image: Фото человека (JPG, PNG)
        cloth_image: Фото одежды (JPG, PNG)
        model_type: "hd" - half-body, "dc" - full-body
        category: 0=upperbody, 1=lowerbody, 2=dress
        scale: масштаб (рекомендуется 1.5-2.5)
        num_steps: шаги инференса
        num_samples: количество результатов
        seed: -1 для случайного, число для воспроизводимости
    """
    # Загрузка изображений из HTTP запроса
    try:
        model_img = Image.open(io.BytesIO(await model_image.read()))
        cloth_img = Image.open(io.BytesIO(await cloth_image.read()))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при чтении изображений: {str(e)}"
        )
    
    # Создание DTO запроса
    request = TryOnRequest(
        model_image=model_img,
        cloth_image=cloth_img,
        model_type=model_type,
        category=category,
        scale=scale,
        num_steps=num_steps,
        num_samples=num_samples,
        seed=seed,
    )
    
    # Выполнение Use Case (бизнес-логика)
    try:
        result = use_case.execute(request)
        return {
            "success": result.success,
            "results": result.results,
            "count": result.count,
        }
    except ValueError as e:
        # Ошибки валидации
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Ошибки выполнения
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при инференсе: {str(e)}"
        )
    

@router.get("/health")
async def health_check(use_case: TryOnUseCase = Depends(get_tryon_use_case)):
    """
    Проверка готовности ML сервиса.
    """
    ml_service = use_case._ml_service
    return ml_service.health_check()
