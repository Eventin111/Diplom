from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _load_project_config_module():
    config_path = Path(__file__).resolve().parents[3] / "Config.py"
    spec = spec_from_file_location("project_config_module", config_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load project Config.py from {config_path}")

    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


project_config_module = _load_project_config_module()
Settings = project_config_module.BackendSettings
project_config = project_config_module.load_project_config()
settings = project_config.backend
