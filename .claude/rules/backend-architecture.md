---
paths:
  - "backend/**/*.py"
---

# Backend Architecture rules

# Layers

| Layer | Path                            | Responsibility                                     |
|---|---------------------------------|----------------------------------------------------|
| Domain | `backend/core/`                 | Business logic. Pure Python only.                  |
| Persistence | `backend/infra/postgresql/`     | SQLAlchemy models + concrete storage implementations |
| Interface | `backend/entrypoints/litestar/` | HTTP handlers, views, auth middleware              |
| DI | `backend/infra/ioc/`            | Dishka providers. Wiring only, no logic            |
| Config | `backend/infra/config/`         | Pydantic settings, logging setup                   |
| File storage | `backend/infra/minio/`          | files adapter                                      |
