from __future__ import annotations

from PIL import Image
import time

from .ports import DiffusionPort, OpenPosePort, ParsingPort
from .entities import InferenceRequest, InferenceResult
from ..utils_ootd import get_mask_location


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
        t0 = time.perf_counter()
        # Load input images
        model_img = Image.open(request.model_path).resize((768, 1024))
        cloth_img = Image.open(request.cloth_path).resize((768, 1024))
        t_load = time.perf_counter()

        # Preprocess
        keypoints = self._openpose.detect(model_img.resize((384, 512)))
        model_parse, _ = self._parsing.parse(model_img.resize((384, 512)))
        t_pre = time.perf_counter()

        category_utils = {
            "upperbody": "upper_body",
            "lowerbody": "lower_body",
            "dress": "dresses",
        }
        if request.model_type == "hd" and request.category != "upperbody":
            raise ValueError("model_type 'hd' requires category 'upperbody'")

        mask, mask_gray = get_mask_location(
            request.model_type,
            category_utils[request.category],
            model_parse,
            keypoints,
        )
        mask = mask.resize((768, 1024), Image.NEAREST)
        mask_gray = mask_gray.resize((768, 1024), Image.NEAREST)

        masked_vton_img = Image.composite(mask_gray, model_img, mask)

        # Run model
        outputs = self._diffusion.generate(
            model_type=request.model_type,
            category=request.category,
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
            f"[OOTD Timing] load={t_load - t0:.2f}s preprocess={t_pre - t_load:.2f}s diffusion={t_gen - t_pre:.2f}s total={t_gen - t0:.2f}s"
        )

        # Return results (no I/O here, caller decides how/where to save)
        return InferenceResult(outputs=outputs, masked_vton=masked_vton_img, mask=mask)
