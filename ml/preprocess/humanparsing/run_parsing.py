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
        available_providers = ort.get_available_providers()
        use_cuda_provider = self.use_cuda and "CUDAExecutionProvider" in available_providers
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if use_cuda_provider else ["CPUExecutionProvider"]

        if use_cuda_provider:
            print(f"[Parsing] Using CUDAExecutionProvider (gpu_id={gpu_id})")
        else:
            print("[Parsing] CUDAExecutionProvider not available in onnxruntime; using CPUExecutionProvider")

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
            providers=providers,
        )
        self.lip_session = ort.InferenceSession(
            os.path.join(
                Path(__file__).absolute().parents[2].absolute(),
                'checkpoints/humanparsing/parsing_lip.onnx',
            ),
            sess_options=session_options,
            providers=providers,
        )

    def __call__(self, input_image):
        if self.use_cuda:
            torch.cuda.set_device(self.gpu_id)
        parsed_image, face_mask = onnx_inference(self.session, self.lip_session, input_image)
        return parsed_image, face_mask
