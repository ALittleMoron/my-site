# Architecture

## Overview

Clean Architecture (Hexagonal). Dependency arrows point inward — domain layer has zero framework dependencies.

```
  ┌─────────────────────────────────────────────┐
  │           entrypoints/litestar/             │  HTTP handlers, views, auth
  │  ┌──────────────────────────────────────┐   │
  │  │              ioc/                    │   │  Dishka DI providers
  │  │  ┌───────────────────────────────┐   │   │
  │  │  │          db/                  │   │   │  SQLAlchemy + Alembic
  │  │  │  ┌────────────────────────┐   │   │   │
  │  │  │  │       core/            │   │   │   │  Pure business logic
  │  │  │  └────────────────────────┘   │   │   │
  │  │  └───────────────────────────────┘   │   │
  │  └──────────────────────────────────────┘   │
  └─────────────────────────────────────────────┘
```

## Layers

### `src/core/` — Domain layer

- Pure Python only. No external library imports, ever.
- Organized by business domain: `auth/`, `blog/`, `competency_matrix/`, `contacts/`, `files/`, `account/`, `markdown/`
- Each domain:
  - `schemas.py` — immutable Pydantic models (domain objects)
  - `use_cases.py` — business logic. Abstract ABC base + concrete `@dataclass(frozen=True, slots=True)`
  - `storages.py` — storage ABC (pure interface, no implementation)
  - `exceptions.py` — domain exceptions
  - `enums.py` — domain enumerations

### `src/db/` — Persistence layer

- SQLAlchemy 2.0 async ORM models in `db/models/`
- Concrete storage implementations in `db/storages/` — each implements the ABC from `core/<domain>/storages.py`
- Alembic migrations in `db/alembic/`
- Session management: async `AsyncSession` with `NullPool` in tests

### `src/entrypoints/litestar/` — Interface layer

- `api/` — REST JSON endpoints (will be consumed by Angular)
- `views/` — Server-rendered HTMX views (temporary, being replaced by Angular)
- `auth.py` — PASETO token middleware
- `guards.py` — Authorization guards
- `initializers.py` — App factory
- `lifespan.py` — Startup/shutdown hooks (runs migrations)
- `cli/` — Litestar CLI commands

### `src/ioc/` — Dependency injection

- Dishka `AsyncContainer` setup
- `container.py` — container factory
- `providers/<domain>_provider.py` — one provider per domain
- Providers inject into handlers via `DishkaRouter`

### `src/config/` — Configuration

- Pydantic settings loaded from environment variables
- `settings.py` — all app config (DB, MinIO, Valkey, auth, etc.)
- `loggers.py` — structlog + ECS setup

### `src/file_storages/` — File storage

- MinIO async client adapter
- Called from use cases via injected interface

## Key patterns

### Use cases

```python
@dataclass(frozen=True, slots=True)
class CreateBlogPost:
    storage: BlogStorage  # injected via DI

    async def execute(self, data: CreateBlogPostSchema) -> BlogPost:
        ...
```

### Storage ABC

```python
# core/blog/storages.py
class BlogStorage(ABC):
    @abstractmethod
    async def create(self, data: CreateBlogPostSchema) -> BlogPost: ...

# db/storages/blog.py
class BlogDatabaseStorage(BlogStorage):
    async def create(self, data: CreateBlogPostSchema) -> BlogPost:
        # SQLAlchemy implementation
```

### DI wiring

```python
# ioc/providers/blog_provider.py
class BlogProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def blog_storage(self, session: AsyncSession) -> BlogStorage:
        return BlogDatabaseStorage(session)

    @provide(scope=Scope.REQUEST)
    async def create_blog_post(self, storage: BlogStorage) -> CreateBlogPost:
        return CreateBlogPost(storage=storage)
```

## Auth

- Stateless PASETO tokens (no server-side sessions yet)
- Token validated by `src/entrypoints/litestar/auth.py` middleware
- Guards in `src/entrypoints/litestar/guards.py` check role from token
- Future: cookie-based sessions (ЭТАП 6)

## Data flow (request lifecycle)

```
HTTP Request
  → Nginx reverse proxy
  → Uvicorn / Litestar
  → Auth middleware (validate PASETO token)
  → Guard (check role if required)
  → Handler (entrypoints/litestar/api/ or views/)
  → Use case (injected by Dishka)
  → Storage (injected — real DB in prod, mock in tests)
  → Response
```
