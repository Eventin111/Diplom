import importlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestGradioModuleImport(unittest.TestCase):
    def test_gradio_module_imports_without_running_server(self):
        # Patch gradio to avoid launching a UI and keep import fast.
        dummy_gr = MagicMock()
        dummy_block = MagicMock()
        dummy_block.queue.return_value = dummy_block
        dummy_block.__enter__.return_value = dummy_block
        dummy_block.__exit__.return_value = False
        dummy_block.launch.return_value = None
        dummy_block.click.return_value = None

        dummy_gr.Blocks.return_value = dummy_block
        dummy_gr.Row.return_value = dummy_block
        dummy_gr.Column.return_value = dummy_block
        dummy_gr.Markdown.return_value = None
        dummy_gr.Image.return_value = None
        dummy_gr.Examples.return_value = None
        dummy_gr.Gallery.return_value = None
        dummy_gr.Button.return_value = dummy_block
        dummy_gr.Slider.return_value = None

        sys.modules["gradio"] = dummy_gr

        # Ensure the `run` directory is importable so `utils_ootd` can be found.
        run_dir = str(Path(__file__).resolve().parents[1] / "run")
        sys.path.insert(0, run_dir)

        # Patch heavy models to dummy ones so import doesn't download weights.
        class DummyModel:
            def __init__(self, *_args, **_kwargs):
                pass

            def __call__(self, *args, **kwargs):
                return []

        with patch("preprocess.openpose.run_openpose.OpenPose", DummyModel), patch(
            "preprocess.humanparsing.run_parsing.Parsing", DummyModel
        ), patch("ootd.inference_ootd_hd.OOTDiffusionHD", DummyModel), patch(
            "ootd.inference_ootd_dc.OOTDiffusionDC", DummyModel
        ):
            # reload in case it was already imported by earlier tests
            if "run.gradio_ootd" in sys.modules:
                del sys.modules["run.gradio_ootd"]
            import run.gradio_ootd as gradio_mod  # noqa: F401

            # Clean up sys.path addition to avoid affecting other tests
            sys.path.remove(run_dir)

            # ensure basic attributes exist
            self.assertTrue(hasattr(gradio_mod, "process_hd"))
            self.assertTrue(hasattr(gradio_mod, "process_dc"))


if __name__ == "__main__":
    unittest.main()
