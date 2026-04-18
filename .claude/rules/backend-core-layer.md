---
paths:
  - "backend/core/**/*.py"
---

# Core layer rules

## Strict import rules — NEVER violate

- `backend/core/**` — NO imports from: sqlalchemy, litestar, dishka, miniopy, pyseto, structlog, sentry_sdk or any third-party packages
- `backend/core/**` — NO imports from: `db/`, `entrypoints/`, `ioc/`, `file_storages/` or any outer layers

## Shared core files (`backend/core/`)

Shared files can be used across all domains.

```
use_cases.py    # Base UseCase(ABC) — all use cases inherit from this
schemas.py      # Shared domain schemas
enums.py        # Shared enums
types.py        # Shared type aliases
exceptions.py   # Shared domain exceptions
generators.py   # Shared generators
```

## Domain structure (per domain in `backend/core/<domain>/`)

Common files — not all present in every domain. Not all files are required.

```
schemas.py              # domain models (dataclasses or class with init dunder method)
use_cases.py            # Business logic - use cases or controllers with not ABC. Only implementations.
storages.py             # Storage ABC - repository pattern (SQLAlchemy, Mongo, etc.)
file_storages.py        # File storages ABC - for manipluating files (MinIO, local files, etc.)
exceptions.py           # Domain exceptions
enums.py                # Domain enumerations
types.py                # Domain type aliases or NewType
services.py             # Domain services - shared business logic, uses in use cases
event_dispatchers.py    # Domain event dispatchers - kafka or rest event publishers
```
