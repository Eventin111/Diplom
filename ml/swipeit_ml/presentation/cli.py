from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from swipeit_ml.application.usecases.run_ootd_inference import RunOOTDInference
from swipeit_ml.domain import ModelType, category_from_index
from swipeit_ml.domain.entities import InferenceRequest
from swipeit_ml.infrastructure.adapters import DiffusionAdapter, OpenPoseAdapter, ParsingAdapter
from swipeit_ml.infrastructure.runtime import get_output_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Run OOTD inference")
    parser.add_argument("--gpu_id", "-g", type=int, default=0, required=False)
    parser.add_argument("--model_path", type=str, default="", required=True)
    parser.add_argument("--cloth_path", type=str, default="", required=True)
    parser.add_argument("--model_type", type=str, default="hd", required=False)
    parser.add_argument("--category", "-c", type=int, default=0, required=False)
    parser.add_argument("--scale", type=float, default=2.0, required=False)
    parser.add_argument("--step", type=int, default=20, required=False)
    parser.add_argument("--sample", type=int, default=4, required=False)
    parser.add_argument("--seed", type=int, default=-1, required=False)
    args = parser.parse_args()

    model_type = ModelType(args.model_type)
    category = category_from_index(args.category)

    if model_type is ModelType.HD and args.category != 0:
        raise ValueError("model_type 'hd' requires category == 0 (upperbody)!")

    request = InferenceRequest(
        gpu_id=args.gpu_id,
        model_type=model_type,
        category=category,
        cloth_path=args.cloth_path,
        model_path=args.model_path,
        image_scale=args.scale,
        num_steps=args.step,
        num_samples=args.sample,
        seed=args.seed,
    )

    openpose = OpenPoseAdapter(args.gpu_id)
    parsing = ParsingAdapter(args.gpu_id)
    diffusion = DiffusionAdapter(args.gpu_id, model_type)

    runner = RunOOTDInference(openpose, parsing, diffusion)
    result = runner.execute(request)

    output_root = get_output_root()
    output_root.mkdir(exist_ok=True)

    if result.mask is not None:
        mask_path = output_root / "mask.jpg"
        result.mask.save(mask_path)
        print("Saved intermediate mask:", mask_path)

    if result.masked_vton is not None:
        mask_vton_path = output_root / "mask_vton.jpg"
        result.masked_vton.save(mask_vton_path)
        print("Saved intermediate masked image:", mask_vton_path)

    output_paths = []
    for idx, image in enumerate(result.outputs):
        path = output_root / f"out_{model_type.value}_{idx}.png"
        image.save(path)
        output_paths.append(path)

    print("Saved outputs:")
    for path in output_paths:
        print(" -", path)


if __name__ == "__main__":
    main()
