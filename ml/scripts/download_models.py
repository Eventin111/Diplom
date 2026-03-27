"""
Скрипт для скачивания весов моделей OOTDiffusion.
"""

from pathlib import Path
from huggingface_hub import hf_hub_download

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHECKPOINTS_DIR = PROJECT_ROOT / "checkpoints"

# Правильные пути (с checkpoints/)
FILES_TO_DOWNLOAD = [
    "checkpoints/ootd/ootd_hd/checkpoint-36000/unet_garm/diffusion_pytorch_model.safetensors",
    "checkpoints/ootd/ootd_hd/checkpoint-36000/unet_vton/diffusion_pytorch_model.safetensors",
    "checkpoints/ootd/ootd_dc/checkpoint-36000/unet_garm/diffusion_pytorch_model.safetensors",
    "checkpoints/ootd/ootd_dc/checkpoint-36000/unet_vton/diffusion_pytorch_model.safetensors",
]


def download_weights():
    print("Скачивание весов OOTDiffusion...")
    print(f"Папка: {CHECKPOINTS_DIR}\n")
    
    CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
    
    for filepath in FILES_TO_DOWNLOAD:
        filename = filepath.split("/")[-1]
        print(f"Скачиваю: {filename}...")
        
        try:
            local_path = hf_hub_download(
                repo_id="levihsu/OOTDiffusion",
                filename=filepath,
                local_dir=str(CHECKPOINTS_DIR),
            )
            print(f"  ✓ {filename}")
        except Exception as e:
            print(f"  ✗ Ошибка: {e}")
    
    print("\nПроверка:")
    for f in (CHECKPOINTS_DIR).rglob("diffusion_pytorch_model*"):
        print(f"  ✓ {f.name} ({f.stat().st_size / 1024 / 1024:.0f} MB)")


if __name__ == "__main__":
    print("=" * 50)
    print("Загрузка весов OOTDiffusion")
    print("=" * 50)
    download_weights()
