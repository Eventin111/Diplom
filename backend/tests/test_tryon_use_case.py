import base64
import importlib
import sys
import types
from io import BytesIO

import pytest
from PIL import Image

from app.application.dto.tryon_dto import TryOnRequest


class DummyMlService:
    def __init__(self, outputs=None):
        self.outputs = outputs or [Image.new("RGB", (16, 16), "blue")]
        self.calls = []

    def try_on(self, **kwargs):
        self.calls.append(kwargs)
        return self.outputs


def load_use_case():
    sys.modules.pop("app.application.use_cases.tryon_use_case", None)
    fake_service_module = types.ModuleType("app.infrastructure.ml.ootd_service")
    fake_service_module.OOTDService = object
    sys.modules["app.infrastructure.ml.ootd_service"] = fake_service_module
    module = importlib.import_module("app.application.use_cases.tryon_use_case")
    return module.TryOnUseCase


def make_request(**overrides):
    payload = {
        "model_image": Image.new("L", (8, 8), 128),
        "cloth_image": Image.new("RGBA", (8, 8), (255, 0, 0, 255)),
        "model_type": "hd",
        "category": 0,
        "scale": 2.0,
        "num_steps": 20,
        "num_samples": 1,
        "seed": -1,
    }
    payload.update(overrides)
    return TryOnRequest(**payload)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("model_type", "bad"),
        ("category", 3),
        ("scale", 0),
        ("scale", 5.1),
        ("num_steps", 0),
        ("num_steps", 101),
        ("num_samples", 0),
        ("num_samples", 11),
    ],
)
def test_validate_rejects_invalid_inputs(field, value):
    TryOnUseCase = load_use_case()
    use_case = TryOnUseCase(DummyMlService())
    request = make_request(**{field: value})

    with pytest.raises(ValueError):
        use_case.validate(request)


def test_validate_rejects_hd_with_non_upperbody():
    TryOnUseCase = load_use_case()
    use_case = TryOnUseCase(DummyMlService())

    with pytest.raises(ValueError):
        use_case.validate(make_request(category=1))


def test_prepare_image_converts_non_rgb():
    TryOnUseCase = load_use_case()
    use_case = TryOnUseCase(DummyMlService())

    result = use_case._prepare_image(Image.new("L", (4, 4), 0))

    assert result.mode == "RGB"


def test_encode_image_to_base64_returns_png_data_uri():
    TryOnUseCase = load_use_case()
    use_case = TryOnUseCase(DummyMlService())

    encoded = use_case._encode_image_to_base64(Image.new("RGB", (3, 2), "green"))

    prefix = "data:image/png;base64,"
    assert encoded.startswith(prefix)
    decoded = base64.b64decode(encoded[len(prefix):])
    restored = Image.open(BytesIO(decoded))
    assert restored.size == (3, 2)
    assert restored.format == "PNG"


def test_execute_prepares_images_calls_ml_service_and_returns_response():
    TryOnUseCase = load_use_case()
    ml_service = DummyMlService(
        outputs=[Image.new("RGB", (10, 10), "white"), Image.new("RGB", (10, 10), "black")]
    )
    use_case = TryOnUseCase(ml_service)

    response = use_case.execute(make_request(num_samples=2, seed=42, scale=1.5))

    assert response.success is True
    assert response.count == 2
    assert len(response.results) == 2
    assert all(item.startswith("data:image/png;base64,") for item in response.results)
    assert len(ml_service.calls) == 1
    call = ml_service.calls[0]
    assert call["model_image"].mode == "RGB"
    assert call["cloth_image"].mode == "RGB"
    assert call["model_type"] == "hd"
    assert call["category"] == 0
    assert call["scale"] == 1.5
    assert call["num_steps"] == 20
    assert call["num_samples"] == 2
    assert call["seed"] == 42
