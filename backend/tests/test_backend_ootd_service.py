import importlib
import sys
import types

import pytest
from PIL import Image


def stub_ml_modules():
    run_pkg = types.ModuleType("run")
    ootd_app_pkg = types.ModuleType("run.ootd_app")
    adapters_module = types.ModuleType("run.ootd_app.adapters")
    entities_module = types.ModuleType("run.ootd_app.entities")
    usecases_module = types.ModuleType("run.ootd_app.usecases")

    class OpenPoseAdapter:
        def __init__(self, gpu_id):
            self.gpu_id = gpu_id

    class ParsingAdapter:
        def __init__(self, gpu_id):
            self.gpu_id = gpu_id

    class DiffusionAdapter:
        def __init__(self, gpu_id, model_type):
            self.gpu_id = gpu_id
            self.model_type = model_type

    class InferenceRequest:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

    class RunOOTDInference:
        def __init__(self, openpose, parsing, diffusion):
            self.openpose = openpose
            self.parsing = parsing
            self.diffusion = diffusion

        def execute(self, request):
            return types.SimpleNamespace(outputs=[Image.new("RGB", (20, 30), "white")])

    adapters_module.OpenPoseAdapter = OpenPoseAdapter
    adapters_module.ParsingAdapter = ParsingAdapter
    adapters_module.DiffusionAdapter = DiffusionAdapter
    entities_module.InferenceRequest = InferenceRequest
    usecases_module.RunOOTDInference = RunOOTDInference

    return {
        "run": run_pkg,
        "run.ootd_app": ootd_app_pkg,
        "run.ootd_app.adapters": adapters_module,
        "run.ootd_app.entities": entities_module,
        "run.ootd_app.usecases": usecases_module,
    }


def load_module(monkeypatch):
    for name, module in stub_ml_modules().items():
        monkeypatch.setitem(sys.modules, name, module)
    sys.modules.pop("app.infrastructure.ml.ootd_service", None)
    return importlib.import_module("app.infrastructure.ml.ootd_service")


def test_health_check_and_singleton(monkeypatch):
    module = load_module(monkeypatch)
    module._service = None

    service = module.get_ootd_service()

    assert service.health_check() == {"status": "ready", "model": "OOTDiffusion"}
    assert module.get_ootd_service() is service


def test_try_on_raises_for_invalid_hd_category(monkeypatch):
    module = load_module(monkeypatch)
    service = module.OOTDService()

    with pytest.raises(ValueError):
        service.try_on(Image.new("RGB", (10, 10)), Image.new("RGB", (10, 10)), model_type="hd", category=1)


def test_try_on_initializes_runner_once_and_returns_outputs(monkeypatch):
    module = load_module(monkeypatch)

    executions = []

    class FakeRunner:
        def __init__(self, openpose, parsing, diffusion):
            self.init_args = (openpose, parsing, diffusion)

        def execute(self, request):
            executions.append(request)
            return types.SimpleNamespace(outputs=[Image.new("RGB", (20, 30), "white")])

    monkeypatch.setattr(module, "RunOOTDInference", FakeRunner)

    service = module.OOTDService(gpu_id=3)
    first = service.try_on(Image.new("RGB", (10, 10)), Image.new("RGB", (10, 10)), model_type="dc", category=2)
    second = service.try_on(Image.new("RGB", (10, 10)), Image.new("RGB", (10, 10)), model_type="dc", category=2)

    assert len(first) == 1
    assert len(second) == 1
    assert len(executions) == 2
    assert executions[0].category == "dress"
    assert service._runner is not None
