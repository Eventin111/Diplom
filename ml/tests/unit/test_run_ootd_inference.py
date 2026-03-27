import unittest

from PIL import Image

from swipeit_ml.application.usecases.run_ootd_inference import RunOOTDInference
from swipeit_ml.domain.entities import InferenceRequest


class DummyOpenPose:
    def detect(self, image: Image.Image) -> dict:
        # Return a minimal keypoints structure compatible with get_mask_location.
        # We return 18 points with coordinates within the image size.
        return {"pose_keypoints_2d": [0, 0] * 18}


class DummyParsing:
    def parse(self, image: Image.Image):
        # Return a dummy parsing image (all zeros) and a placeholder value.
        return Image.new("L", image.size), None


class DummyDiffusion:
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
    ):  # pragma: no cover
        # Return a fixed number of output images for testing.
        return [Image.new("RGB", image_ori.size, "white") for _ in range(num_samples)]


class TestRunOOTDInference(unittest.TestCase):
    def test_execute_returns_expected_outputs(self):
        request = InferenceRequest(
            gpu_id=0,
            model_type="hd",
            category="upperbody",
            cloth_path="",
            model_path="",
            image_scale=1.0,
            num_steps=1,
            num_samples=2,
            seed=0,
        )

        usecase = RunOOTDInference(DummyOpenPose(), DummyParsing(), DummyDiffusion())

        # Monkeypatch image loading to avoid file I/O.
        # We replace Image.open with a fixed-size image.
        from PIL import Image as PILImage

        original_open = PILImage.open

        def fake_open(path):
            return Image.new("RGB", (768, 1024), "black")

        PILImage.open = fake_open
        try:
            result = usecase.execute(request)
        finally:
            PILImage.open = original_open

        self.assertEqual(len(result.outputs), 2)
        for out_img in result.outputs:
            self.assertEqual(out_img.size, (768, 1024))

        self.assertIsNotNone(result.mask)
        self.assertIsNotNone(result.masked_vton)
        self.assertEqual(result.mask.size, (768, 1024))
        self.assertEqual(result.masked_vton.size, (768, 1024))


if __name__ == "__main__":
    unittest.main()
