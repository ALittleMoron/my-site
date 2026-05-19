# CLAUDE.md

## Project

Portfolio/blog site and knowledge database

## Stack

- Runtime: Python 3.14, uv
- Framework: Litestar 2.18+
- DB: PostgreSQL 16 + SQLAlchemy 2.0 async + Alembic
- DI: Dishka
- Cache: Valkey
- File storage: MinIO (miniopy-async)
- Auth: PASETO (pyseto) + Argon2 password hashing
- Logging: structlog + ECS logging + Sentry SDK
- Frontend: Angular 19 SPA + Bootstrap 5, served by a frontend-owned nginx image
- Edge: nginx reverse proxy for TLS, `/api/*`, frontend, MinIO, and backup UI routing

## General rules

- Always use Context7 when I need library/API documentation, code generation, setup or configuration steps without me having to explicitly ask.
