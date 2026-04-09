from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "ml"))
sys.path.insert(0, str(Path(__file__).parent))

from app.application.dto.tryon_dto import TryOnRequest
from app.application.use_cases.tryon_use_case import TryOnUseCase
from app.infrastructure.ml.ootd_service import get_ootd_service


def _load_image(image_path: str) -> Image.Image:
    image = Image.open(image_path)
    image.load()
    return image


def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("Usage: python backend/run_tryon_job.py <payload.json> <result.json>")

    payload_path = Path(sys.argv[1])
    result_path = Path(sys.argv[2])
    payload = json.loads(payload_path.read_text(encoding="utf-8"))

    request = TryOnRequest(
        model_image=_load_image(str(payload["model_image_path"])),
        cloth_image=_load_image(str(payload["cloth_image_path"])),
        model_type=str(payload["model_type"]),
        category=int(payload["category"]),
        scale=float(payload["scale"]),
        num_steps=int(payload["num_steps"]),
        num_samples=int(payload["num_samples"]),
        seed=int(payload["seed"]),
    )

    use_case = TryOnUseCase(get_ootd_service())
    result = use_case.execute(request)
    result_path.write_text(
        json.dumps(
            {
                "results": list(result.results),
                "count": int(result.count),
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
