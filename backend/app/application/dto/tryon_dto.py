"""
DTO (Data Transfer Objects) для Try-On модуля.
"""

from dataclasses import dataclass
from typing import Optional

from PIL import Image


@dataclass
class TryOnRequest:
    """
    DTO для запроса на виртуальную примерку.
    """

    model_image: Image.Image
    cloth_image: Image.Image
    model_type: str = "hd"
    category: int = 0
    scale: float = 2.0
    num_steps: int = 4
    num_samples: int = 1
    seed: int = -1


@dataclass
class TryOnResponse:
    """
    DTO для ответа виртуальной примерки.
    """

    success: bool
    results: list[str]  # URLs или base64
    count: int
    error: Optional[str] = None
