from __future__ import annotations

from typing import Any

from PIL import Image

from swipeit_ml.application.ports import ParsingPort
from swipeit_ml.infrastructure.runtime.paths import ensure_third_party_on_path

ensure_third_party_on_path()

from preprocess.humanparsing.run_parsing import Parsing


class ParsingAdapter(ParsingPort):
    def __init__(self, gpu_id: int):
        self._impl = Parsing(gpu_id)

    def parse(self, image: Image.Image) -> tuple[Image.Image, Any]:
        return self._impl(image)
