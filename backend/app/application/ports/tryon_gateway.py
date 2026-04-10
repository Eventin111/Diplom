from __future__ import annotations

from typing import Protocol

from PIL import Image


class TryOnGateway(Protocol):
    def try_on(
        self,
        *,
        model_image: Image.Image,
        cloth_image: Image.Image,
        model_type: str,
        category: int,
        scale: float,
        num_steps: int,
        num_samples: int,
        seed: int,
    ) -> list[Image.Image]:
        """Run the try-on inference and return generated images."""
