from __future__ import annotations

import time

from PIL import Image

from swipeit_ml.application.ports import DiffusionPort, OpenPosePort, ParsingPort
from swipeit_ml.application.services.masking import get_mask_location
from swipeit_ml.domain.entities import InferenceRequest, InferenceResult
from swipeit_ml.domain.enums import (
    CATEGORY_TO_MASK_CATEGORY,
    GarmentCategory,
    ModelType,
    coerce_category,
    coerce_model_type,
)


class RunOOTDInference:
    def __init__(
        self,
        openpose: OpenPosePort,
        parsing: ParsingPort,
        diffusion: DiffusionPort,
    ):
        self._openpose = openpose
        self._parsing = parsing
        self._diffusion = diffusion

    def execute(self, request: InferenceRequest) -> InferenceResult:
        model_type = coerce_model_type(request.model_type)
        category = coerce_category(request.category)

        t0 = time.perf_counter()
        model_img = Image.open(request.model_path).resize((768, 1024))
        cloth_img = Image.open(request.cloth_path).resize((768, 1024))
        t_load = time.perf_counter()

        keypoints = self._openpose.detect(model_img.resize((384, 512)))
        model_parse, _ = self._parsing.parse(model_img.resize((384, 512)))
        t_pre = time.perf_counter()

        if model_type is ModelType.HD and category is not GarmentCategory.UPPERBODY:
            raise ValueError("model_type 'hd' requires category 'upperbody'")

        mask, mask_gray = get_mask_location(
            model_type.value,
            CATEGORY_TO_MASK_CATEGORY[category],
            model_parse,
            keypoints,
        )
        mask = mask.resize((768, 1024), Image.NEAREST)
        mask_gray = mask_gray.resize((768, 1024), Image.NEAREST)

        masked_vton_img = Image.composite(mask_gray, model_img, mask)

        outputs = self._diffusion.generate(
            model_type=model_type.value,
            category=category.value,
            image_garm=cloth_img,
            image_vton=masked_vton_img,
            mask=mask,
            image_ori=model_img,
            num_samples=request.num_samples,
            num_steps=request.num_steps,
            image_scale=request.image_scale,
            seed=request.seed,
        )
        t_gen = time.perf_counter()

        print(
            (
                f"[OOTD Timing] load={t_load - t0:.2f}s "
                f"preprocess={t_pre - t_load:.2f}s "
                f"diffusion={t_gen - t_pre:.2f}s "
                f"total={t_gen - t0:.2f}s"
            )
        )

        return InferenceResult(outputs=outputs, masked_vton=masked_vton_img, mask=mask)
