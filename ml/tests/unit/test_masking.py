import unittest

import numpy as np
from PIL import Image

from swipeit_ml.application.services.masking import (
    extend_arm_mask,
    get_mask_location,
    hole_fill,
    refine_mask,
)


class TestUtilsOOTD(unittest.TestCase):
    def test_extend_arm_mask_simple(self):
        wrist = np.array([10.0, 0.0])
        elbow = np.array([5.0, 0.0])
        assert np.allclose(extend_arm_mask(wrist, elbow, 2.0), np.array([15.0, 0.0]))

    def test_hole_fill_and_refine_mask(self):
        # create a simple mask with a hole
        img = np.zeros((10, 10), dtype=np.uint8)
        img[2:8, 2:8] = 255
        img[4:6, 4:6] = 0

        filled = hole_fill(img)
        self.assertEqual(filled.dtype, np.uint8)
        self.assertTrue(np.all(filled[4:6, 4:6] == 255))

        refined = refine_mask(filled)
        self.assertEqual(refined.dtype, np.uint8)
        # should still contain foregroud region
        self.assertTrue(np.any(refined == 255))

    def _make_parse_image(self, label_value: int) -> Image.Image:
        arr = np.full((512, 384), label_value, dtype=np.uint8)
        return Image.fromarray(arr)

    def test_get_mask_location_upper_body(self):
        # make a parse image with upper clothes label
        parse_img = self._make_parse_image(4)

        keypoints = {
            "pose_keypoints_2d": [0.0, 0.0] * 18,
        }

        mask, mask_gray = get_mask_location("hd", "upper_body", parse_img, keypoints)
        self.assertIsInstance(mask, Image.Image)
        self.assertIsInstance(mask_gray, Image.Image)

    def test_get_mask_location_invalid_model_type(self):
        parse_img = self._make_parse_image(0)
        keypoints = {"pose_keypoints_2d": [0.0, 0.0] * 18}
        with self.assertRaises(ValueError):
            get_mask_location("invalid", "upper_body", parse_img, keypoints)

    def test_get_mask_location_invalid_category(self):
        parse_img = self._make_parse_image(0)
        keypoints = {"pose_keypoints_2d": [0.0, 0.0] * 18}
        with self.assertRaises(NotImplementedError):
            get_mask_location("hd", "unknown", parse_img, keypoints)
