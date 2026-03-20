from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
LOCAL_MEDIA_ROOT = PROJECT_ROOT / "backend" / "local_media"


def ensure_local_media_dir() -> Path:
    LOCAL_MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    return LOCAL_MEDIA_ROOT


def build_local_media_path(storage_key: str) -> Path:
    root = ensure_local_media_dir()
    return root / storage_key
