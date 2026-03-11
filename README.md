# SwipeIt 👕👗

Приложение для подбора одежды с виртуальной примеркой (Virtual Try-On) на базе **OOTDiffusion**.

## 🛠 Технологический стек

- **Backend**: FastAPI (Python 3.10)
- **ML**: OOTDiffusion (PyTorch 2.0+)
- **Database**: PostgreSQL
- **Storage**: MinIO (S3-совместимое хранилище)

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-repo/swipeit.git
cd swipeit
```

### 2. Настройка Python (3.10)

```bash
conda create -n swipeit python=3.10
conda activate swipeit
```

### 3. Установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 4. Настройка окружения

Создай файл `.env` в папке `backend/`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/swipeit
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=your-access-key
MINIO_SECRET_KEY=your-secret-key
MINIO_BUCKET_NAME=swipeit
MINIO_SECURE=false
SECRET_KEY=generate-secure-random-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

> ⚠️ **Важно**: Замени значения на свои безопасные!

### 5. Запуск БД и MinIO

```bash
docker-compose up -d postgres minio
```

### 6. Запуск сервера

```bash
cd backend
python run_server.py
```

Сервер: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

## 👗 Virtual Try-On

### Установка ML зависимостей

```bash
pip install torch==2.0.1 torchvision==0.15.2
```

### Загрузка моделей

```bash
cd ml
python download_models.py
```

### API

```
POST /api/v1/tryon
```

Параметры (multipart/form-data):
- `person_image` — фото человека
- `cloth_image` — фото одежды
- `model_type` — `hd` (полутело) или `dc` (полное тело)

## 📁 Структура

```
swipeit/
├── backend/           # FastAPI
│   ├── app/api/v1/   # Endpoints
│   ├── run_server.py
│   └── requirements.txt
├── ml/                # OOTDiffusion
│   ├── ootd/         # Инференс
│   └── download_models.py
└── docker-compose.yml
```

## ⚠️ Требования

| Режим | RAM |
|-------|-----|
| CPU (half-body) | 8GB+ |
| CPU (full-body) | 16GB+ |

## 📝 Лицензия

MIT
