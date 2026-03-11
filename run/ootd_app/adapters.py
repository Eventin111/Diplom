from __future__ import annotations

from pathlib import Path
from typing import Any
from PIL import Image

from preprocess.openpose.run_openpose import OpenPose
from preprocess.humanparsing.run_parsing import Parsing

from ootd.inference_ootd import OOTDiffusion

from .ports import DiffusionPort, OpenPosePort, ParsingPort


class OpenPoseAdapter(OpenPosePort):
    def __init__(self, gpu_id: int):
        self._impl = OpenPose(gpu_id)

    def detect(self, image: Image.Image) -> dict:
        return self._impl(image)


class ParsingAdapter(ParsingPort):
    def __init__(self, gpu_id: int):
        self._impl = Parsing(gpu_id)

    def parse(self, image: Image.Image) -> tuple[Image.Image, Any]:
        return self._impl(image)


class DiffusionAdapter(DiffusionPort):
    def __init__(self, gpu_id: int, model_type: str):
        self._model_type = model_type
        self._diffusion = OOTDiffusion(
            gpu_id=gpu_id,
            unet_checkpoint_path=self._get_unet_checkpoint(model_type),
        )

    def _get_unet_checkpoint(self, model_type: str) -> Path:
        repo_root = Path(__file__).resolve().parents[2]
        if model_type == "hd":
            return repo_root / "checkpoints/ootd/ootd_hd/checkpoint-36000"
        elif model_type == "dc":
            return repo_root / "checkpoints/ootd/ootd_dc/checkpoint-36000"
        raise ValueError("model_type must be 'hd' or 'dc'")

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
        return self._diffusion(
            model_type=model_type,
            category=category,
            image_garm=image_garm,
            image_vton=image_vton,
            mask=mask,
            image_ori=image_ori,
            num_samples=num_samples,
            num_steps=num_steps,
            image_scale=image_scale,
            seed=seed,
        )
