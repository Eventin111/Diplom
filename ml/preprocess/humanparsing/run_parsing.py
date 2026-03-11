import pdb
from pathlib import Path
import sys
import os

# Optional dependencies; tests should be able to import this module even if they are missing.
try:
    import onnxruntime as ort
    import torch
except ImportError:  # pragma: no cover
    ort = torch = None

PROJECT_ROOT = Path(__file__).absolute().parents[0].absolute()
sys.path.insert(0, str(PROJECT_ROOT))
from parsing_api import onnx_inference


class Parsing:
    def __init__(self, gpu_id: int):
        if ort is None or torch is None:
            raise ImportError(
                "Parsing requires 'onnxruntime' and 'torch'. Install requirements or use a mock for tests."
            )

        self.gpu_id = gpu_id
        self.use_cuda = torch.cuda.is_available()
        if self.use_cuda:
            torch.cuda.set_device(gpu_id)
        else:
            print("[Parsing] CUDA not available; running on CPU")
        session_options = ort.SessionOptions()
        session_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        session_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        session_options.add_session_config_entry('gpu_id', str(gpu_id))
        self.session = ort.InferenceSession(
            os.path.join(
                Path(__file__).absolute().parents[2].absolute(),
                'checkpoints/humanparsing/parsing_atr.onnx',
            ),
            sess_options=session_options,
            providers=['CPUExecutionProvider'],
        )
        self.lip_session = ort.InferenceSession(
            os.path.join(
                Path(__file__).absolute().parents[2].absolute(),
                'checkpoints/humanparsing/parsing_lip.onnx',
            ),
            sess_options=session_options,
            providers=['CPUExecutionProvider'],
        )

    def __call__(self, input_image):
        if self.use_cuda:
            torch.cuda.set_device(self.gpu_id)
        parsed_image, face_mask = onnx_inference(self.session, self.lip_session, input_image)
        return parsed_image, face_mask
