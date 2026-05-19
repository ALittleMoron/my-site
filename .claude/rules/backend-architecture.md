---
paths:
  - "backend/**/*.py"
---

# Backend Architecture rules

# Layers

| Layer | Path                                | Responsibility                                     |
|---|-------------------------------------|----------------------------------------------------|
| Domain | `backend/src/core/`                 | Business logic. Pure Python only.                  |
| Persistence | `backend/src/infra/postgresql/`     | SQLAlchemy models + concrete storage implementations |
| Interface | `backend/src/entrypoints/litestar/` | HTTP handlers, API endpoints, auth middleware      |
| DI | `backend/src/infra/ioc/`            | Dishka providers. Wiring only, no logic            |
| Config | `backend/src/infra/config/`         | Pydantic settings, logging setup                   |
| File storage | `backend/src/infra/minio/`          | files adapter                                      |
