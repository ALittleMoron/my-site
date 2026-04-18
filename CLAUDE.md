# CLAUDE.md

## Project: Portfolio/blog site

## Stack

- Runtime: Python 3.14, uv
- Framework: Litestar 2.18+
- DB: PostgreSQL 16 + SQLAlchemy 2.0 async + Alembic
- DI: Dishka
- Cache: Valkey
- File storage: MinIO (miniopy-async)
- Auth: PASETO (pyseto) + Argon2 password hashing
- Logging: structlog + ECS logging + Sentry SDK
- Frontend: HTMX 2 + Jinja2 + Bootstrap 5 + Hyperscript (→ Angular, planned)

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

### Strict import rules — NEVER violate

- `backend/entrypoints/**` — NO direct imports from `db/`. Only through `core/` abstractions via DI
- `backend/db/storages/**` — MUST implement the ABC defined in the corresponding `core/<domain>/storages.py`
- `backend/ioc/**` — wiring only; importing and instantiating providers is the only job

Note: the providers directory in `backend/ioc/` is misspelled as `prodivers/` in the codebase.
