# Clean Architecture Status

Этот файл фиксирует текущее состояние репозитория с точки зрения Clean Architecture и помогает планировать следующий рефакторинг без потери работоспособности.

## Общая оценка

- Репозиторий в целом: `72/100`
- Backend: `78/100`
- Frontend: `68/100`
- ML: `80/100`

Оценка субъективная, но опирается на текущую структуру слоев, реальные импорты и объём совместимых shim-слоев.

## Backend

Сильные стороны:

- Явно выделены `presentation`, `application`, `domain`, `infrastructure`.
- Try-on use case уже зависит от application port, а не от concrete ML-класса.
- Очередь, кэш, rate-limit и maintenance-сценарии вынесены в `infrastructure`.

Что ещё мешает считать backend "чистым":

- `presentation/api/v1/*` по-прежнему напрямую собирает репозитории и технические сервисы вместо orchestration через application service/use case.
- В `app/core` остаются shim-модули и shared utilities; это лучше, чем толстый `core`, но слой ещё не доведён до минимального.
- В `backend/scripts/*` есть прямые импорты старых shared-точек вроде `app.core.db`.

## Frontend

Сильные стороны:

- Есть `core/domain`, `core/application`, `core/infrastructure`.
- Auth, try-on, likes и media уже заведены через use case + repository.
- `pages` больше не ходят напрямую в `services/api/*` для этих сценариев.

Что ещё мешает считать frontend "чистым":

- `pages` остаются очень толстыми и держат много orchestration/UI state в одном месте.
- `services/api/*` пока ещё существуют как слой совместимости; это полезно для миграции, но не финальное состояние.
- Не все сценарии ещё перенесены на единый application flow и composition root.

## ML

Сильные стороны:

- Появился отдельный пакет `ml/swipeit_ml` со слоями `domain`, `application`, `infrastructure`.
- Внутри `infrastructure` появились отдельные подпакеты `adapters`, `config`, `runtime`.
- `swipeit_ml/presentation/*` стал единым presentation-слоем без однофайловых shim-обёрток.
- Legacy/vendor-код вынесен в `ml/third_party/*`, а backend-адаптер уже использует новую ML-структуру.
- Тесты разложены на `ml/tests/unit` и `ml/tests/integration`.

Что ещё мешает считать ML "чистым":

- В репозитории всё ещё живёт большой объём legacy/vendor-кода OOTDiffusion и human parsing tooling.
- В `third_party/preprocess/humanparsing/mhp_extension/*` по-прежнему много training/research-артефактов, не относящихся к inference path.
- Нет отдельного слоя для конфигурации/DI контейнера; зависимости собираются прямо в presentation/infrastructure.

## Порядок В Репозитории

Что уже в порядке:

- Основные generated/runtime директории добавлены в `.gitignore`.
- Build/output артефакты не попали в индекс Git в текущем состоянии.
- Рефакторинг идёт маленькими коммитами по отдельным архитектурным срезам.

Что ещё стоит довести:

- Убрать или свести к минимуму shim-слой в `backend/app/core`.
- Довести frontend до feature-oriented composition поверх `core/application`.
- Отдельно пройтись по `ml/third_party/preprocess/*` и удалить реально неиспользуемые training/demo-only артефакты.
- Определить судьбу локальных рабочих заметок вроде `LOCAL_CLEAN_ARCHITECTURE_NOTES.md`.

## Следующий Приоритет

1. Backend: убрать оставшиеся legacy-импорты из `backend/scripts/*` и довести `core` до truly-shared utilities.
2. Frontend: перенести оставшиеся сценарии из compatibility-facade слоя в единый application flow.
3. ML: проверить `third_party/preprocess/humanparsing/mhp_extension/*` и удалить то, что не нужно для inference path.
