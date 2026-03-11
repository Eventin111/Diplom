import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image


class DummyOpenPoseImpl:
    def __init__(self, gpu_id):
        self.gpu_id = gpu_id

    def __call__(self, image):
        return {"pose_keypoints_2d": [0.0, 0.0] * 18}

    def detect(self, image):
        # For adapter usage in RunOOTDInference
        return self.__call__(image)


class DummyParsingImpl:
    def __init__(self, gpu_id):
        self.gpu_id = gpu_id

    def __call__(self, image):
        return image, None

    def parse(self, image):
        return self.__call__(image)


class DummyDiffusionImpl:
    def __init__(self, gpu_id, unet_checkpoint_path):
        self.gpu_id = gpu_id
        self.unet_checkpoint_path = unet_checkpoint_path

    def __call__(
        self,
        model_type,
        category,
        image_garm,
        image_vton,
        mask,
        image_ori,
        num_samples,
        num_steps,
        image_scale,
        seed,
    ):
        # Return a list of dummy images corresponding to num_samples
        return [Image.new("RGB", (768, 1024), "black") for _ in range(num_samples)]


class DummyDiffusionAdapter:
    def __init__(self, gpu_id, model_type):
        self.gpu_id = gpu_id
        self.model_type = model_type

    def generate(
        self,
        model_type,
        category,
        image_garm,
        image_vton,
        mask,
        image_ori,
        num_samples,
        num_steps,
        image_scale,
        seed,
    ):
        return [Image.new("RGB", (768, 1024), "black") for _ in range(num_samples)]


class TestAdaptersAndEntrypoint(unittest.TestCase):
    def test_adapters_use_underlying_impl(self):
        import run.ootd_app.adapters as adapters

        with patch("run.ootd_app.adapters.OpenPose", DummyOpenPoseImpl), patch(
            "run.ootd_app.adapters.Parsing", DummyParsingImpl
        ), patch("run.ootd_app.adapters.OOTDiffusion", DummyDiffusionImpl):
            openpose = adapters.OpenPoseAdapter(gpu_id=0)
            parsing = adapters.ParsingAdapter(gpu_id=0)
            diffusion = adapters.DiffusionAdapter(gpu_id=0, model_type="hd")

            self.assertEqual(openpose.detect(None)["pose_keypoints_2d"][0], 0.0)
            parsed, _ = parsing.parse(None)
            self.assertIsNone(_)
            outputs = diffusion.generate(
                model_type="hd",
                category="upperbody",
                image_garm=Image.new("RGB", (768, 1024)),
                image_vton=Image.new("RGB", (768, 1024)),
                mask=Image.new("L", (768, 1024)),
                image_ori=Image.new("RGB", (768, 1024)),
                num_samples=2,
                num_steps=1,
                image_scale=1.0,
                seed=0,
            )
            self.assertEqual(len(outputs), 2)

    def test_run_ootd_main_uses_adapters(self):
        import run.run_ootd as run_ootd

        with tempfile.TemporaryDirectory() as tmpdir:
            model_path = f"{tmpdir}/model.png"
            cloth_path = f"{tmpdir}/cloth.png"
            Image.new("RGB", (768, 1024), "black").save(model_path)
            Image.new("RGB", (768, 1024), "black").save(cloth_path)

            with patch("run.run_ootd.OpenPoseAdapter", lambda gpu_id: DummyOpenPoseImpl(gpu_id)), patch(
                "run.run_ootd.ParsingAdapter", lambda gpu_id: DummyParsingImpl(gpu_id)
            ), patch(
                "run.run_ootd.DiffusionAdapter",
                lambda gpu_id, model_type: DummyDiffusionAdapter(gpu_id, model_type),
            ), patch(
                "run.ootd_app.usecases.get_mask_location",
                lambda *_args, **_kwargs: (Image.new("L", (768, 1024)), Image.new("L", (768, 1024))),
            ), patch(
                "sys.argv",
                [
                    "run_ootd.py",
                    "--model_path",
                    model_path,
                    "--cloth_path",
                    cloth_path,
                    "--model_type",
                    "hd",
                    "--category",
                    "0",
                ],
            ):
                run_ootd.main()


if __name__ == "__main__":
    unittest.main()
