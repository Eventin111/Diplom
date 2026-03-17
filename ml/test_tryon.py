# cd D:\Projects\SwipeIt
# python ml/test_tryon.py

"""
Тест Try-On без FastAPI.
Запустить: python ml/test_tryon.py
"""

from pathlib import Path
import sys
from PIL import Image

# Добавляем пути
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "ml"))

from ml.ootd_service import OOTDService

# Папки с примерами
EXAMPLES_DIR = PROJECT_ROOT / "ml" / "run" / "examples"
MODEL_DIR = EXAMPLES_DIR / "model"
GARMENT_DIR = EXAMPLES_DIR / "garment"
OUTPUT_DIR = PROJECT_ROOT / "ml" / "run" / "images_output"
OUTPUT_DIR.mkdir(exist_ok=True)


def main():
    print("=" * 50)
    print("Тест OOTDiffusion")
    print("=" * 50)
    
    # Берём первые изображения из папок
    model_files = list(MODEL_DIR.glob("*.jpg")) + list(MODEL_DIR.glob("*.png"))
    garment_files = list(GARMENT_DIR.glob("*.jpg")) + list(GARMENT_DIR.glob("*.png"))
    
    if not model_files:
        print(f"\n❌ Нет изображений в {MODEL_DIR}")
        return
    
    if not garment_files:
        print(f"\n❌ Нет изображений в {GARMENT_DIR}")
        return
    
    MODEL_IMAGE = model_files[0]
    CLOTH_IMAGE = garment_files[0]
    
    print(f"\n📷 Использую изображения:")
    print(f"  Модель: {MODEL_IMAGE.name}")
    print(f"  Одежда: {CLOTH_IMAGE.name}")
    
    model_img = Image.open(MODEL_IMAGE).convert("RGB")
    cloth_img = Image.open(CLOTH_IMAGE).convert("RGB")
    
    # Уменьшаем изображения для экономии памяти
    max_size = 256
    model_img.thumbnail((max_size, max_size))
    cloth_img.thumbnail((max_size, max_size))
    
    print(f"  Размер модели: {model_img.size} (уменьшено для экономии памяти)")
    print(f"  Размер одежды: {cloth_img.size}")
    
    print(f"\n🚀 Создаю сервис...")
    service = OOTDService(gpu_id=0)
    
    print(f"\n⚙️ Запускаю инференс (на CPU это займёт время)...")
    print("  num_samples=1, num_steps=2 для быстрого теста")
    
    # В функции try_on замени print на более подробный вывод:
    print(f"  num_samples=1, num_steps=2 для быстрого теста")

    # Добавь try-except для отладки:
    import sys
    try:
        print("→ Вызов service.try_on()...", flush=True)
        results = service.try_on(
            model_image=model_img,
            cloth_image=cloth_img,
            model_type="hd",
            category=0,
            scale=2.0,
            num_steps=2,
            num_samples=1,
            seed=42,
        )
        print(f"\n✅ Получено {len(results)} результатов!", flush=True)
        
        # Сохраняем
        for i, img in enumerate(results):
            output_path = OUTPUT_DIR / f"test_result_{i}.png"
            img.save(output_path)
            print(f"  Сохранено: {output_path}", flush=True)
    except Exception as e:
        import traceback
        print(f"\n❌ Ошибка: {e}", flush=True)
        traceback.print_exc()
        results = []
    
    print("\n" + "=" * 50)
    print("Тест завершён!")
    print("=" * 50)


if __name__ == "__main__":
    main()
