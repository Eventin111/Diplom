import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock


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

        ml_root = str(Path(__file__).resolve().parents[2])
        sys.path.insert(0, ml_root)

        # Reload in case it was already imported by earlier tests.
        if "swipeit_ml.presentation.gradio_demo" in sys.modules:
            del sys.modules["swipeit_ml.presentation.gradio_demo"]
        import swipeit_ml.presentation.gradio_demo as gradio_mod  # noqa: F401

        # Clean up sys.path addition to avoid affecting other tests
        sys.path.remove(ml_root)

        # Importing the module should not initialize heavy models eagerly.
        self.assertTrue(hasattr(gradio_mod, "process_hd"))
        self.assertTrue(hasattr(gradio_mod, "process_dc"))
        self.assertIsNone(gradio_mod.OpenPose)
        self.assertIsNone(gradio_mod.Parsing)
        self.assertIsNone(gradio_mod.OOTDiffusionHD)
        self.assertIsNone(gradio_mod.OOTDiffusionDC)


if __name__ == "__main__":
    unittest.main()
