from __future__ import annotations

from pathlib import Path

from swipeit_ml.domain.enums import ModelType, coerce_model_type
from swipeit_ml.infrastructure.runtime.paths import get_project_root


def get_unet_checkpoint_path(model_type: ModelType | str) -> Path:
    normalized_model_type = coerce_model_type(model_type)
    checkpoints_root = get_project_root() / "checkpoints" / "ootd"

    if normalized_model_type is ModelType.HD:
        return checkpoints_root / "ootd_hd" / "checkpoint-36000"
    if normalized_model_type is ModelType.DC:
        return checkpoints_root / "ootd_dc" / "checkpoint-36000"
    raise ValueError("model_type must be 'hd' or 'dc'")
