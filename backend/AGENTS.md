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

## Operation Boundaries

- Do not model entity mutation methods as `upsert` when the behavior can create, update,
  delete, or otherwise mutate different state. Use explicit operation-specific names and methods
  such as `create_*`, `update_*`, `delete_*`, `publish_*`, or `set_*` so callers cannot
  accidentally trigger broader behavior than intended.

## Business Logic Boundaries

- Business logic must live in domain use cases under `backend/src/core/**/use_cases.py`.
  Shared domain behavior may live in explicit core domain services when a use case would otherwise
  duplicate meaningful logic.
- API controllers, Litestar handlers, schemas, Dishka providers, storages, ORM models, settings,
  event dispatchers, and infrastructure adapters must not own business decisions. They may validate
  transport shape, map data, wire dependencies, persist/load data, or call a use case.
- Request-level access checks and input checks that can be decided before entering a use case should
  live at the Litestar boundary, preferably as guards or `Provide` dependencies. Do not hide those
  checks in controller helper functions.
- Do not add private module-level helper functions in backend source to hold business behavior.
  Put the behavior on the real owning class or use case instead.
- Do not create classes that exist only to wrap one or more `@classmethod` helpers. A class must
  represent a real domain concept, interface, adapter, provider, guard, schema, model, or service.
- Top-level functions are acceptable when the framework or tool naturally requires them or when a
  callable class would add ceremony without improving ownership: app factories, Litestar lifespan
  hooks, CLI commands, Alembic migration functions, and small pure infrastructure entrypoints.
- When choosing between a function and a method, prefer the shape that expresses real ownership.
  Do not move code into a class solely to satisfy a stylistic ban on functions.

## HTTP and Schemas

- API controllers must contain only HTTP validation, auth/permission checks, use case calls, and request/response mapping.
- Controllers must receive dependencies through `FromDishka[...]`, preferably typed as abstract use case interfaces.
- API schemas must inherit from the shared schema bases and explicitly map to/from domain objects with `to_schema` / `from_domain_schema`.
- Use `to_domain_schema` / `from_domain_schema` for same-concept conversions between API schemas, ORM models, and core domain schemas when the method signature already identifies the exact source/target type. Use a more specific conversion method name only when the conversion changes the semantic entity, such as attached resource -> plain external resource.
- Do not pass Pydantic API schemas, SQLAlchemy models, or Litestar types into the core layer.

## I18n

- The backend i18n catalog is the source of truth for UI interface strings and enum labels.
  Database/content localisation is out of scope until an explicit design change says otherwise.
- Supported UI languages must be modeled with a backend enum. Do not accept arbitrary language
  strings in production API/settings code.
- The default UI language must be configured explicitly through the required
  `I18N_DEFAULT_LANGUAGE` environment setting; do not add production defaults for it.
- Keep the available-languages endpoint and bundle endpoint consistent with the enum and catalog,
  and cover new languages/keys with catalog parity tests.

## Persistence

- SQLAlchemy models and database storages live only under `backend/src/infra/postgresql/`.
- Database storages return domain schemas, not ORM models.
- Storages may `flush`, but must not `commit`; transaction ownership belongs to the DI/session provider.
- Every DB model change must include a matching Alembic migration.

## Dependency Injection

- Dishka providers are wiring only: no business logic, DB queries, or external side effects.
- Use `Scope.APP` only for stateless singleton-safe dependencies; use `Scope.REQUEST` for sessions, storages, and use cases.
