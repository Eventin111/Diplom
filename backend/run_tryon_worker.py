"""
Скрипт запуска Redis worker для очереди try-on задач.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "ml"))
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _prepend_ld_library_path(path_value: str) -> None:
    if not path_value:
        return
    current = os.getenv("LD_LIBRARY_PATH", "")
    paths = [segment for segment in current.split(":") if segment]
    if path_value in paths:
        return
    os.environ["LD_LIBRARY_PATH"] = ":".join([path_value, *paths])


def ensure_cuda_loader_compat() -> None:
    """
    WSL+Docker иногда монтирует только libcuda.so.1.
    Часть библиотек (cuDNN/torch extensions) ищет именно libcuda.so.
    """
    candidate_dirs = [
        Path("/usr/lib/wsl/lib"),
        Path("/usr/lib/x86_64-linux-gnu"),
        Path("/usr/local/nvidia/lib64"),
        Path("/usr/local/nvidia/lib"),
    ]

    for parent in (Path("/usr/lib/wsl/drivers"),):
        if parent.exists():
            candidate_dirs.extend(path.parent for path in parent.rglob("libcuda.so.1"))

    seen = set()
    unique_dirs: list[Path] = []
    for path in candidate_dirs:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        unique_dirs.append(path)

    for directory in unique_dirs:
        libcuda_v1 = directory / "libcuda.so.1"
        libcuda = directory / "libcuda.so"
        if libcuda_v1.exists():
            _prepend_ld_library_path(str(directory))
            if not libcuda.exists():
                try:
                    libcuda.symlink_to(libcuda_v1.name)
                    logger.info("Created CUDA loader alias: %s -> %s", libcuda, libcuda_v1.name)
                except OSError as exc:
                    logger.debug("Failed to create CUDA loader alias in %s: %s", directory, exc)


def configure_cpu_limits() -> None:
    os.environ.setdefault("OMP_NUM_THREADS", "2")
    os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
    os.environ.setdefault("MKL_NUM_THREADS", "2")
    os.environ.setdefault("NUMEXPR_NUM_THREADS", "2")
    os.environ.setdefault("TORCH_NUM_THREADS", "2")
    os.environ.setdefault("TORCH_NUM_INTEROP_THREADS", "1")

    try:
        import torch

        torch.set_num_threads(int(os.getenv("TORCH_NUM_THREADS", "2")))
        torch.set_num_interop_threads(int(os.getenv("TORCH_NUM_INTEROP_THREADS", "1")))
    except Exception:
        pass

    try:
        import cv2

        cv2.setNumThreads(1)
    except Exception:
        pass


if __name__ == "__main__":
    ensure_cuda_loader_compat()
    configure_cpu_limits()

    from app.infrastructure.workers.tryon_worker import run_tryon_worker

    asyncio.run(run_tryon_worker())
