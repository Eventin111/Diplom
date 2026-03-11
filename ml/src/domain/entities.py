from dataclasses import dataclass
from typing import List

@dataclass
class TryOnResult:
    generated_images: List[str]   # пути к сгенерированным картинкам