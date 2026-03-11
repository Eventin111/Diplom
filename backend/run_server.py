"""
Скрипт запуска сервера с поддержкой ML.
"""

import os
import sys
from pathlib import Path

# Добавляем КОРЕНЬ проекта в PYTHONPATH (где лежит ml/)
project_root = Path(__file__).parent.parent  # D:\Projects\SwipeIt
sys.path.insert(0, str(project_root))

# Добавляем ml/ для импорта OOTDiffusion
ml_path = project_root / "ml"
sys.path.insert(0, str(ml_path))

# Добавляем корень backend
backend_root = Path(__file__).parent
sys.path.insert(0, str(backend_root))

print(f"PYTHONPATH: {sys.path[:3]}...")

# Теперь запускаем uvicorn
import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )