from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any
from PIL import Image


class OpenPosePort(ABC):
    @abstractmethod
    def detect(self, image: Image.Image) -> dict:
        """Run keypoint detection on a single image."""


class ParsingPort(ABC):
    @abstractmethod
    def parse(self, image: Image.Image) -> tuple[Image.Image, Any]:
        """Run human parsing and return the parsing map (and optional extras)."""


class DiffusionPort(ABC):
    @abstractmethod
    def generate(
        self,
        model_type: str,
        category: str,
        image_garm: Image.Image,
        image_vton: Image.Image,
        mask: Image.Image,
        image_ori: Image.Image,
        num_samples: int,
        num_steps: int,
        image_scale: float,
        seed: int,
    ) -> list[Image.Image]:
        """Generate a set of output images from the configured model."""
