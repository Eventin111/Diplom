from __future__ import annotations

from typing import Any

from PIL import Image

from swipeit_ml.application.ports import ParsingPort
from swipeit_ml.infrastructure.runtime.paths import ensure_third_party_on_path

ensure_third_party_on_path()

Parsing = None


def _get_parsing_cls():
    global Parsing
    if Parsing is None:
        from preprocess.humanparsing.run_parsing import Parsing as _Parsing

        Parsing = _Parsing
    return Parsing


class ParsingAdapter(ParsingPort):
    def __init__(self, gpu_id: int):
        self._impl = _get_parsing_cls()(gpu_id)

    def parse(self, image: Image.Image) -> tuple[Image.Image, Any]:
        return self._impl(image)
