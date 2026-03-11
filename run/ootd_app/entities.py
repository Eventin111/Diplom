from __future__ import annotations

from dataclasses import dataclass
from PIL import Image


@dataclass
class InferenceRequest:
    gpu_id: int
    model_type: str
    category: str
    cloth_path: str
    model_path: str
    image_scale: float
    num_steps: int
    num_samples: int
    seed: int


@dataclass
class InferenceResult:
    # Generated output images (in-memory) from the model.
    outputs: list[Image.Image]

    # Mask images created during preprocessing (optional).
    masked_vton: Image.Image | None = None
    mask: Image.Image | None = None
