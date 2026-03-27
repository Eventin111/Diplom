from __future__ import annotations

from PIL import Image

from swipeit_ml.application.ports import DiffusionPort
from swipeit_ml.domain.enums import ModelType
from swipeit_ml.infrastructure.config.checkpoints import get_unet_checkpoint_path
from swipeit_ml.infrastructure.runtime.paths import ensure_third_party_on_path

ensure_third_party_on_path()

OOTDiffusion = None


def _get_ootd_diffusion_cls():
    global OOTDiffusion
    if OOTDiffusion is None:
        from ootd.inference_ootd import OOTDiffusion as _OOTDiffusion

        OOTDiffusion = _OOTDiffusion
    return OOTDiffusion


class DiffusionAdapter(DiffusionPort):
    def __init__(self, gpu_id: int, model_type: ModelType | str):
        self._diffusion = _get_ootd_diffusion_cls()(
            gpu_id=gpu_id,
            unet_checkpoint_path=get_unet_checkpoint_path(model_type),
        )

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
