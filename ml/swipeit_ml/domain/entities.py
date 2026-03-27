from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from swipeit_ml.domain.enums import GarmentCategory, ModelType


@dataclass
class InferenceRequest:
    gpu_id: int
    model_type: ModelType | str
    category: GarmentCategory | str
    cloth_path: str
    model_path: str
    image_scale: float
    num_steps: int
    num_samples: int
    seed: int


@dataclass
class InferenceResult:
    outputs: list[Image.Image]
    masked_vton: Image.Image | None = None
    mask: Image.Image | None = None
