from __future__ import annotations

from PIL import Image

from swipeit_ml.application.ports import OpenPosePort
from swipeit_ml.infrastructure.runtime.paths import ensure_third_party_on_path

ensure_third_party_on_path()

from preprocess.openpose.run_openpose import OpenPose


class OpenPoseAdapter(OpenPosePort):
    def __init__(self, gpu_id: int):
        self._impl = OpenPose(gpu_id)

    def detect(self, image: Image.Image) -> dict:
        return self._impl(image)
