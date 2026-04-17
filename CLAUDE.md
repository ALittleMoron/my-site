# CLAUDE.md

## Project

Portfolio/blog site. Python 3.14, Litestar 2.x, Clean Architecture.
Frontend: HTMX 2 + Jinja2 (server-side rendering, migrating to Angular — see Roadmap).

## General rules

- Always use Context7 when I need library/API documentation, code generation, setup or configuration steps without me having to explicitly ask.

## Architecture

### Layers

| Layer | Path | Responsibility                                       |
|---|---|------------------------------------------------------|
| Domain | `backend/core/` | Business logic. Pure Python only.                    |
| Persistence | `backend/db/` | SQLAlchemy models + concrete storage implementations |
| Interface | `backend/entrypoints/litestar/` | HTTP handlers, views, auth middleware                |
| DI | `backend/ioc/` | Dishka providers. Wiring only, no logic              |
| Config | `backend/config/` | Pydantic settings, logging setup                     |
| File storage | `backend/file_storages/` | files adapter (MinIO, local files, etc.)             |

### Shared core files (`backend/core/`)

```
use_cases.py    # Base UseCase(ABC) — all use cases inherit from this
schemas.py      # Shared domain schemas
enums.py        # Shared enums (e.g. PublishStatusEnum)
types.py        # Shared type aliases
exceptions.py   # Shared domain exceptions
generators.py   # Shared generators
```

### Domain structure (per domain in `backend/core/<domain>/`)

Common files — not all present in every domain:
```
schemas.py              # domain models (dataclasses or class with init dunder method)
use_cases.py            # Business logic — abstract ABC + concrete @dataclass(frozen=True, slots=True)
storages.py             # Storage ABC (or file_storages.py for the files domain)
exceptions.py           # Domain exceptions
enums.py                # Domain enumerations (if needed)
types.py                # Domain type aliases (if needed)
services.py             # Domain services - shared business logic (if needed)
event_dispatchers.py    # Domain event dispatchers - kafka or rest event publishers (if needed)
```

### Strict import rules — NEVER violate

- `backend/core/**` — NO imports from: sqlalchemy, litestar, dishka, miniopy, pyseto, structlog, sentry_sdk or any third-party packages
- `backend/core/**` — NO imports from: `db/`, `entrypoints/`, `ioc/`, `file_storages/` or any outer layers
- `backend/core/**` — MAY import from: `config.loggers` (structlog wrapper — logging is the one allowed exception)
- `backend/entrypoints/**` — NO direct imports from `db/`. Only through `core/` abstractions via DI
- `backend/db/storages/**` — MUST implement the ABC defined in the corresponding `core/<domain>/storages.py`
- `backend/ioc/**` — wiring only; importing and instantiating providers is the only job

Note: the providers directory in `backend/ioc/` is misspelled as `prodivers/` in the codebase.

## Stack

| | |
|---|---|
| Runtime | Python 3.14, uv |
| Framework | Litestar 2.18+ |
| DB | PostgreSQL 16 + SQLAlchemy 2.0 async + Alembic |
| DI | Dishka |
| Cache | Valkey |
| File storage | MinIO (miniopy-async) |
| Auth | PASETO (pyseto) + Argon2 password hashing |
| Logging | structlog + ECS logging + Sentry SDK |
| Frontend | HTMX 2 + Jinja2 + Bootstrap 5 + Hyperscript (→ Angular, planned) |

## Development Workflow

### Database changes

```bash
make revision "description"   # autogenerate migration
make migrate                  # upgrade head
make downgrade                # rollback -1
```

### Local dev

```bash
make run            # full stack via docker compose
make start_local_app  # app only (needs local PG/Valkey/MinIO)
make shell          # IPython REPL with autoreload
```

### Before commit

```bash
make quality  # bandit + vulture + fix + types + ruff-check + all tests
```

## Testing

### Philosophy

TDD. Tests drive implementation. Unit tests cover all logic branches. Integration tests cover success paths only.

### Split by directory

| Type | Definition | Directory |
|---|---|---|
| **Unit** | Single layer in isolation. Uses mock storages/providers. | `tests/unit/` |
| **Integration** | DB storages + core together, no mocks. Happy path only. | `tests/integration/` |

### Commands

```bash
make test-unit           # unit tests only (fast, run often)
make test-integration    # integration tests (needs DB running)
make tests               # all tests
make tests-coverage      # all + coverage report
```

### Patterns

- Shared fixtures: `tests/fixtures.py` — `FactoryFixture`, `StorageFixture`
- Unit-only fixtures: `tests/unit/fixtures.py` — `ContainerFixture`, `ApiFixture` (re-exports `FactoryFixture`)
- Mock providers for unit tests: `tests/unit/mocks/providers/`
- Test data factories in `tests/helpers/factories/`: `CoreFactoryHelper` (domain objects), `ApiFactoryHelper` (request payloads) — plain Python, no Mimesis
- Access via `self.factory.core.*` / `self.factory.api.*` — inherit from `FactoryFixture`
- Unit test mocking: `Mock(spec=SomeStorageABC)` from `unittest.mock`
- API tests: inherit `ApiFixture` → `self.api.*` / `self.no_auth_api.*`
- Integration (DB) tests: inherit `StorageFixture` → `self.storage_helper.*`, session auto-rollbacks

### Coverage target

**95%** — driven by unit tests. Integration tests don't count toward this.
Current threshold in pyproject.toml: 60% (temporary, raise as unit tests grow).

Core layer should be 100% coverage.

## Code Style

- line-length: 100 (ruff + black)
- ruff: ALL rules, see ignores in pyproject.toml
- mypy: strict mode (`disallow_untyped_defs = true` etc.)
- No docstrings unless interface is non-obvious from types
- Comments: only for non-obvious WHY, never WHAT
