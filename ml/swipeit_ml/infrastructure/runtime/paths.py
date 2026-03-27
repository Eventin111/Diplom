from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
THIRD_PARTY_ROOT = PROJECT_ROOT / "third_party"
EXAMPLES_ROOT = PROJECT_ROOT / "examples"
OUTPUT_ROOT = PROJECT_ROOT / "images_output"


def ensure_project_root_on_path() -> Path:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    return PROJECT_ROOT


def ensure_third_party_on_path() -> Path:
    ensure_project_root_on_path()
    if str(THIRD_PARTY_ROOT) not in sys.path:
        sys.path.insert(0, str(THIRD_PARTY_ROOT))
    return THIRD_PARTY_ROOT


def get_project_root() -> Path:
    return PROJECT_ROOT


def get_examples_root() -> Path:
    return EXAMPLES_ROOT


def get_output_root() -> Path:
    return OUTPUT_ROOT
