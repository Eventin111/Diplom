"""Backend server entrypoint."""

from __future__ import annotations

import sys
from pathlib import Path

import uvicorn


def _bootstrap_paths() -> None:
    project_root = Path(__file__).parent.parent
    backend_root = Path(__file__).parent
    ml_path = project_root / "ml"

    for path in (project_root, ml_path, backend_root):
        path_str = str(path)
        if path_str not in sys.path:
            sys.path.insert(0, path_str)


def main() -> None:
    _bootstrap_paths()

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
