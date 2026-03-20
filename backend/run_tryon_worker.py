"""
Скрипт запуска Redis worker для очереди try-on задач.
"""

import asyncio
import logging
import sys
from pathlib import Path


project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "ml"))
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)

from app.infrastructure.workers.tryon_worker import run_tryon_worker


if __name__ == "__main__":
    asyncio.run(run_tryon_worker())
