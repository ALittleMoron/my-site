# Backend Instructions

These rules apply to backend Python code under `backend/**/*.py`.

## Code Style

- line-length: 100 (ruff + black)
- ruff: ALL rules, see ignores in `pyproject.toml`
- mypy: strict mode (`disallow_untyped_defs = true` etc.)
- No docstrings unless interface is non-obvious from types
- Comments: only for non-obvious WHY, never WHAT

## Layers

| Layer | Path | Responsibility |
|---|---|---|
| Domain | `backend/src/core/` | Business logic. Pure Python only. |
| Persistence | `backend/src/infra/postgresql/` | SQLAlchemy models + concrete storage implementations |
| Interface | `backend/src/entrypoints/litestar/` | HTTP handlers, API endpoints, auth middleware |
| DI | `backend/src/infra/ioc/` | Dishka providers. Wiring only, no logic |
| Config | `backend/src/infra/config/` | Pydantic settings, logging setup |
| File storage | `backend/src/infra/minio/` | files adapter |

## HTTP and Schemas

- API controllers must contain only HTTP validation, auth/permission checks, use case calls, and request/response mapping.
- Controllers must receive dependencies through `FromDishka[...]`, preferably typed as abstract use case interfaces.
- API schemas must inherit from the shared schema bases and explicitly map to/from domain objects with `to_schema` / `from_domain_schema`.
- Use `to_domain_schema` / `from_domain_schema` for same-concept conversions between API schemas, ORM models, and core domain schemas when the method signature already identifies the exact source/target type. Use a more specific conversion method name only when the conversion changes the semantic entity, such as attached resource -> plain external resource.
- Do not pass Pydantic API schemas, SQLAlchemy models, or Litestar types into the core layer.

## Persistence

- SQLAlchemy models and database storages live only under `backend/src/infra/postgresql/`.
- Database storages return domain schemas, not ORM models.
- Storages may `flush`, but must not `commit`; transaction ownership belongs to the DI/session provider.
- Every DB model change must include a matching Alembic migration.

## Dependency Injection

- Dishka providers are wiring only: no business logic, DB queries, or external side effects.
- Use `Scope.APP` only for stateless singleton-safe dependencies; use `Scope.REQUEST` for sessions, storages, and use cases.
