# Swipelt Frontend

Frontend часть дипломного проекта с разделением по Clean Architecture, мок-инфраструктурой и unit-тестами.

## Что реализовано

- `Clean Architecture` для ключевой бизнес-логики:
  - `src/core/domain` - сущности и правила
  - `src/core/application` - use-cases
  - `src/core/infrastructure` - репозитории, storage, мок-данные
  - `src/pages`, `src/components`, `src/context` - presentation layer
- Единая конфигурация:
  - `src/config/appConfig.js` - интерфейс к переменным окружения внутри frontend
  - `src/config/index.js` - единая точка экспорта frontend-конфига
- Unit-тесты для domain/application/infrastructure/utils.
- Покрытие тестами контролируется через Jest `coverageThreshold >= 70%`.

## Особенности текущей версии

- Проект работает на мок-данных (`REACT_APP_USE_MOCK_DATA=true` по умолчанию).
- Прямой интеграции с backend сейчас нет (нет согласованных портов/API endpoint'ов).
- Auth и часть API реализованы через mock-repositories, чтобы фронт оставался воспроизводимым автономно.

## Быстрый старт

```bash
cd frontend
npm install
npm start
```

Приложение поднимется на `http://localhost:3000`.

## Переменные окружения

Скопируйте `.env.example` в `.env` и при необходимости измените:

```bash
REACT_APP_NAME=Swipelt
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_USE_MOCK_DATA=true
REACT_APP_MOCK_DELAY_MS=200
REACT_APP_AUTH_INIT_DELAY_MS=300
```

## Тесты и покрытие

```bash
cd frontend
npm run test
npm run test:coverage
```

Порог покрытия:

- branches >= 70%
- functions >= 70%
- lines >= 70%
- statements >= 70%

## Как воспроизвести результат

1. Запустить `npm start`.
2. Открыть страницу логина.
3. Войти тестовым пользователем:
   - email: `test@mail.ru`
   - password: `123456`
4. Либо выбрать гостевой вход.
5. Проверить ленту, профиль и регистрацию (все данные сохраняются в `localStorage`).

