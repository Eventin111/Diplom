# Backend Architecture

## Overview

Backend is organized in a Clean Architecture-like structure with explicit layers:

- `presentation`
  HTTP layer: FastAPI routers and API schemas.
- `application`
  Use cases and internal DTOs.
- `domain`
  Business concepts and rules shared across the system.
- `infrastructure`
  Technical adapters: database, repositories, queue, cache, storage, auth, ML, workers.
- `core`
  Shared config and utility modules used by multiple layers.

This is not strict textbook Clean Architecture, but the dependency flow is intentionally kept close to:

```text
presentation -> application -> domain
presentation -> infrastructure
application -> domain
application -> infrastructure
infrastructure -> domain
core -> shared support
```

## Current Structure

```text
backend/
  app/
    presentation/
      api/
        schemas/
        v1/
    application/
      dto/
      use_cases/
    domain/
      enums/
    infrastructure/
      auth/
      cache/
      db/
      ml/
      persistence/
        models/
        repositories/
      queue/
      storage/
      workers/
    core/
    main.py
```

## Layer Responsibilities

### `presentation`

Path: [backend/app/presentation](/d:/Projects/SwipeIt/backend/app/presentation)

Contains:

- FastAPI routers in [backend/app/presentation/api/v1](/d:/Projects/SwipeIt/backend/app/presentation/api/v1)
- HTTP request/response schemas in [backend/app/presentation/api/schemas](/d:/Projects/SwipeIt/backend/app/presentation/api/schemas)

This layer should:

- accept HTTP requests
- validate and serialize API payloads
- call application use cases and infrastructure services
- return HTTP responses

This layer should not:

- contain SQLAlchemy logic
- implement ML inference
- own database access details

### `application`

Path: [backend/app/application](/d:/Projects/SwipeIt/backend/app/application)

Contains:

- use cases in [backend/app/application/use_cases](/d:/Projects/SwipeIt/backend/app/application/use_cases)
- internal DTOs in [backend/app/application/dto](/d:/Projects/SwipeIt/backend/app/application/dto)

This layer contains scenario-level logic such as:

- try-on orchestration inputs
- internal create/update contracts for repositories
- business flow composition

### `domain`

Path: [backend/app/domain](/d:/Projects/SwipeIt/backend/app/domain)

Contains:

- shared business enums in [backend/app/domain/enums](/d:/Projects/SwipeIt/backend/app/domain/enums)

Examples:

- `TryOnStatus`
- `TryOnEventType`

This layer should stay independent from FastAPI and SQLAlchemy as much as practical.

### `infrastructure`

Path: [backend/app/infrastructure](/d:/Projects/SwipeIt/backend/app/infrastructure)

Contains technical adapters and runtime mechanisms:

- DB engine and schema compatibility: [backend/app/infrastructure/db](/d:/Projects/SwipeIt/backend/app/infrastructure/db)
- ORM models and repositories: [backend/app/infrastructure/persistence](/d:/Projects/SwipeIt/backend/app/infrastructure/persistence)
- Redis queue and client: [backend/app/infrastructure/queue](/d:/Projects/SwipeIt/backend/app/infrastructure/queue)
- Cache helpers: [backend/app/infrastructure/cache](/d:/Projects/SwipeIt/backend/app/infrastructure/cache)
- S3/local storage adapters: [backend/app/infrastructure/storage](/d:/Projects/SwipeIt/backend/app/infrastructure/storage)
- Auth adapter: [backend/app/infrastructure/auth](/d:/Projects/SwipeIt/backend/app/infrastructure/auth)
- ML adapter: [backend/app/infrastructure/ml](/d:/Projects/SwipeIt/backend/app/infrastructure/ml)
- Background workers: [backend/app/infrastructure/workers](/d:/Projects/SwipeIt/backend/app/infrastructure/workers)

### `core`

Path: [backend/app/core](/d:/Projects/SwipeIt/backend/app/core)

Contains shared support code:

- config
- hashing
- image processing
- logging
- orchestration helpers that are still shared across flows

`core` is intentionally small and should not become a dump for all technical code.

## Main Runtime Flows

### API startup

- Entry point: [backend/run_server.py](/d:/Projects/SwipeIt/backend/run_server.py)
- App module: [backend/app/main.py](/d:/Projects/SwipeIt/backend/app/main.py)

### Try-on worker

- Entry point: [backend/run_tryon_worker.py](/d:/Projects/SwipeIt/backend/run_tryon_worker.py)
- Worker implementation: [backend/app/infrastructure/workers/tryon_worker.py](/d:/Projects/SwipeIt/backend/app/infrastructure/workers/tryon_worker.py)

### Database migrations

- Alembic config: [backend/alembic.ini](/d:/Projects/SwipeIt/backend/alembic.ini)
- Alembic env: [backend/alembic/env.py](/d:/Projects/SwipeIt/backend/alembic/env.py)
- Migration runner: [backend/run_migrations.py](/d:/Projects/SwipeIt/backend/run_migrations.py)

## Testing

Backend tests are in [backend/tests](/d:/Projects/SwipeIt/backend/tests).

Run all backend tests:

```powershell
python -m pytest backend/tests -q
```

## Developer Notes

- Old shim packages like `app.api`, `app.models`, `app.repositories`, `app.schemas`, `app.workers` were removed after import migration.
- Runtime code now imports directly from the clean layers.
- Service scripts are grouped in [backend/scripts](/d:/Projects/SwipeIt/backend/scripts) instead of being scattered in the backend root.

## Practical Summary

If you need to find something quickly:

- API endpoint: `presentation/api/v1`
- API schema: `presentation/api/schemas`
- use case: `application/use_cases`
- internal DTO: `application/dto`
- business enum: `domain/enums`
- ORM model: `infrastructure/persistence/models`
- repository: `infrastructure/persistence/repositories`
- Redis/S3/auth/ML adapter: `infrastructure/*`
- worker: `infrastructure/workers`
