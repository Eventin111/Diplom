from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[3]
LOCAL_MEDIA_ROOT = BACKEND_ROOT / "local_media"
LEGACY_LOCAL_MEDIA_ROOT = BACKEND_ROOT / "backend" / "local_media"


def ensure_local_media_dir() -> Path:
    LOCAL_MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
    return LOCAL_MEDIA_ROOT


def build_local_media_path(storage_key: str) -> Path:
    local_path = ensure_local_media_dir() / storage_key
    legacy_path = LEGACY_LOCAL_MEDIA_ROOT / storage_key
    if legacy_path.exists() and not local_path.exists():
        return legacy_path
    return local_path
