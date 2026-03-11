@echo off
echo [1/4] Stopping previous containers...
docker-compose down

echo [2/4] Starting Docker services...
docker-compose up -d

echo [3/4] Waiting for services to start ...
timeout /t 10 /nobreak >nul

echo [4/4] Checking services...
docker-compose ps

echo.
echo [DONE] All services are running!
echo.
echo FastAPI:     http://localhost:8000
echo Swagger UI: http://localhost:8000/docs
echo MinIO:       http://localhost:9001
echo PostgreSQL:  localhost:5432
echo.
echo To start backend:
echo   cd backend
echo   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo To stop: docker-compose down
pause