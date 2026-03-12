# SwipeIt 👕👗

Приложение для подбора одежды с виртуальной примеркой (Virtual Try-On) на базе **OOTDiffusion**.

## 🛠 Технологический стек

- **Backend**: FastAPI (Python 3.10)
- **ML**: OOTDiffusion (PyTorch 2.0+)
- **Frontend**: React 18 + React Router
- **Database**: PostgreSQL
- **Storage**: MinIO (S3-совместимое хранилище)

## 🚀 Быстрый старт

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-repo/swipeit.git
cd swipeit/Diplom
```

### 2. Настройка Python (3.10)

```bash
conda create -n swipeit python=3.10
conda activate swipeit
```

### 3. Установка зависимостей backend + ml

```bash
pip install -r requirements.txt
```

### 4. Настройка окружения

Создай файл `.env` в папке `backend/`:

```env
DB_URL=postgresql://postgres:swipeit-gon-make-it@localhost:5432/swipeit
SECRET_KEY=generate-secure-random-key
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin123
S3_BUCKET_NAME=swipeit-media
S3_REGION=us-east-1
S3_SECURE=false
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=["http://localhost:3000"]
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

> ⚠️ **Важно**: Замени значения на свои безопасные!

### 5. Запуск БД и MinIO

```bash
docker-compose up -d postgres minio redis
```

### 6. Запуск backend

```bash
cd backend
python run_server.py
```

Сервер: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

### 7. Запуск frontend

```bash
cd frontend
npm install
npm start
```

Frontend: `http://localhost:3000`

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

```text
Diplom/
├── backend/           # FastAPI
│   ├── app/api/v1/    # Endpoints
│   ├── run_server.py
│   └── app/core/config.py
├── ml/                # OOTDiffusion
│   ├── run/           # Инференс
│   └── download_models.py
├── frontend/          # React frontend
│   ├── src/core/      # Clean Architecture (domain/app/infra)
│   ├── src/config/    # Конфигурация фронта
│   ├── src/pages/
│   └── src/components/
├── docker-compose.yml
└── requirements.txt
```

## ⚠️ Требования

| Режим | RAM |
|-------|-----|
| CPU (half-body) | 8GB+ |
| CPU (full-body) | 16GB+ |

## 📝 Лицензия

MIT
