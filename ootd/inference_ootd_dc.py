from pathlib import Path

from .inference_ootd import OOTDiffusion

REPO_ROOT = Path(__file__).resolve().parents[1]
UNET_PATH = REPO_ROOT / "checkpoints/ootd/ootd_dc/checkpoint-36000"

class OOTDiffusionDC(OOTDiffusion):

    def __init__(self, gpu_id):
        super().__init__(gpu_id, unet_checkpoint_path=UNET_PATH)
