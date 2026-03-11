from dataclasses import dataclass

@dataclass
class TryOnRequest:
    person_image_path: str
    cloth_image_path: str
    scale: float = 2.0
    num_samples: int = 4
    model_type: str = "hd"          # "hd" или "dc"
    category: int | None = None     # 0=upper, 1=lower, 2=dress
    steps: int = 20
    seed: int | None = None