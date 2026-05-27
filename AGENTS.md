# AGENTS.md

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
- Do not perform any git action that changes repository state unless I explicitly ask for it. This includes `git add`, `git commit`, `git push`, `git stash`, branch creation, branch switching, rebasing, merging, resetting, checking out files, and similar mutating operations.
- For non-trivial tasks, create and follow a Superpowers implementation plan before changing code or configuration. Trivial docs-only edits and direct answers do not require a plan.
- Implement behavior changes and bug fixes with TDD by default: add or update the failing test first, then make it pass. If a test is not practical for the change, state why before implementing.
- Before finishing implementation work, do a self-review/code-review pass focused on bugs, regressions, missing tests, and instruction compliance.
- Before claiming completion, run the relevant checks through existing `make` targets: tests, linters, type checks, format checks, migrations, or local-run checks as applicable. For broad or cross-cutting changes, run the full practical check suite. If any relevant check is skipped, explain why in the final response.
- After each code or configuration change, explicitly check whether infrastructure, documentation, CI/CD, and relevant `AGENTS.md` instructions must be updated; keep them consistent with the change.
  - At minimum, search related terms in `docs/`, `.github/`, root README-style files, and nested `AGENTS.md` files before finishing.
  - If no documentation, infrastructure, CI/CD, or instruction updates are needed, mention that check in the final response.
- Use existing `make` targets for installation, checks, tests, migrations, and local runs when available instead of calling lower-level tools directly.
- Do not change lock files (`backend/uv.lock`, `frontend/package-lock.json`) unless dependencies intentionally changed.
- Do not commit secrets, real tokens, private keys, or `.env` values. Configuration must flow through environment-backed settings.
- Treat Docker and nginx changes as infrastructure changes: preserve the split where edge nginx routes domains and `/api/*`, while frontend nginx serves the SPA and falls back to `index.html`.
- When a Superpowers plan is completed, remove the finished plan files from `docs/superpowers/plans/`.
- More specific instructions live in nested `AGENTS.md` files under `backend/`, `backend/src/core/`, `backend/tests/`, `frontend/`, and `frontend/src/app/`.
