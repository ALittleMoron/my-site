# Core Layer Instructions

These rules apply to backend core code under `backend/src/core/**/*.py`.

## Strict Import Rules

Never violate these boundaries:

- `backend/src/core/**` must not import `sqlalchemy`, `litestar`, `dishka`, `miniopy`, `pyseto`, `structlog`, `sentry_sdk`, or any third-party packages.
- `backend/src/core/**` must not import from `infra/postgresql/`, `entrypoints/`, `infra/ioc/`, `infra/minio`, or any outer layers.
- Do not add new imports from `infra.config` or logging into core; pass configurable values through parameters or injected abstractions.

## Shared Core Files

Shared files can be used across all domains.

```text
use_cases.py    # Base UseCase(ABC) — all use cases inherit from this
schemas.py      # Shared domain schemas
enums.py        # Shared enums
types.py        # Shared type aliases
exceptions.py   # Shared domain exceptions
generators.py   # Shared generators
```

## Domain Structure

Common files per domain in `backend/core/<domain>/`. Not all files are required.

```text
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

## Domain Rules

- New core code must be domain dataclasses, value objects, use cases, services, interfaces, exceptions, or generators.
- Core exceptions must express domain failures; HTTP representation belongs at the entrypoint boundary.
- Do not log secrets, password hashes, tokens, raw credentials, or other sensitive values.
