import tempfile
import unittest

from PIL import Image

from swipeit_ml.application.usecases.run_ootd_inference import RunOOTDInference
from swipeit_ml.domain.entities import InferenceRequest


class DummyOpenPose:
    def detect(self, image):
        # Return minimal keypoints (18 points with zeros)
        return {"pose_keypoints_2d": [0.0, 0.0] * 18}


class DummyParsing:
    def parse(self, image):
        # Return the same image and a dummy mask
        return image, None


class DummyDiffusion:
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
        # Make a predictable output image
        out = Image.new("RGB", (10, 10), "red")
        return [out for _ in range(num_samples)]


class TestUsecases(unittest.TestCase):
    def test_run_ootd_inference_returns_images(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two simple image files for model and cloth
            model_path = f"{tmpdir}/model.png"
            cloth_path = f"{tmpdir}/cloth.png"
            # Use grayscale images so parsing output is single-channel (avoid cv2 channel errors).
            Image.new("L", (768, 1024), 0).save(model_path)
            Image.new("L", (768, 1024), 0).save(cloth_path)

            request = InferenceRequest(
                gpu_id=0,
                model_type="hd",
                category="upperbody",
                cloth_path=cloth_path,
                model_path=model_path,
                image_scale=2.0,
                num_steps=5,
                num_samples=2,
                seed=0,
            )

            usecase = RunOOTDInference(DummyOpenPose(), DummyParsing(), DummyDiffusion())
            result = usecase.execute(request)

            self.assertEqual(len(result.outputs), 2)
            for img in result.outputs:
                self.assertIsInstance(img, Image.Image)

    def test_run_ootd_inference_hd_requires_upperbody(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = f"{tmpdir}/dummy.png"
            Image.new("L", (768, 1024), 0).save(file_path)
            request = InferenceRequest(
                gpu_id=0,
                model_type="hd",
                category="lowerbody",
                cloth_path=file_path,
                model_path=file_path,
                image_scale=2.0,
                num_steps=1,
                num_samples=1,
                seed=0,
            )

            usecase = RunOOTDInference(DummyOpenPose(), DummyParsing(), DummyDiffusion())
            with self.assertRaises(ValueError):
                usecase.execute(request)
