# AGENTS.md

## Project

Portfolio/notes site and knowledge database

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

- When library/API documentation, code generation, setup, or configuration steps are needed, search the internet without me having to explicitly ask. Prefer official documentation and primary sources, and cite the sources used in the response.
- Do not perform any git action that changes repository state unless I explicitly ask for it. This includes `git add`, `git commit`, `git push`, `git stash`, branch creation, branch switching, rebasing, merging, resetting, checking out files, and similar mutating operations.
- For non-trivial tasks, create and follow a Superpowers implementation plan before changing code or configuration. Trivial docs-only edits and direct answers do not require a plan.
- If a task turns out to be large enough to risk context degradation, split it into explicit subtasks and run sequential subagents for those subtasks. Each subagent must start its assigned subtask atomically, with a narrow scope and clear handoff back to the main thread.
- Implement behavior changes and bug fixes with TDD by default: add or update the failing test first, then make it pass. If a test is not practical for the change, state why before implementing.
- Do not add default values in real production code. API parameters, schemas, dataclasses, settings, helpers, services, and infrastructure-facing code should require callers or environment configuration to pass values explicitly. Tests, test helpers, and factories may keep defaults when they make test setup clearer.
- Before finishing implementation work, do a self-review/code-review pass focused on bugs, regressions, missing tests, and instruction compliance.
- Before claiming completion, run the relevant checks through existing `make` targets: tests, linters, type checks, format checks, migrations, or local-run checks as applicable. For broad or cross-cutting changes, run the full practical check suite. If any relevant check is skipped, explain why in the final response.
- After each code or configuration change, explicitly check whether infrastructure, documentation, CI/CD, and relevant `AGENTS.md` instructions must be updated; keep them consistent with the change.
  - At minimum, search related terms in `docs/`, `.github/`, root README-style files, and nested `AGENTS.md` files before finishing.
  - After every code, configuration, documentation, infrastructure, or instruction change, explicitly ask whether the change should be captured in the relevant `AGENTS.md`. Do not silently decide that `AGENTS.md` does not need an update.
  - If no documentation, infrastructure, CI/CD, or instruction updates are needed, mention that check in the final response.
- Use existing `make` targets for installation, checks, tests, migrations, and local runs when available instead of calling lower-level tools directly.
- Keep Makefiles as thin wrappers only: Make recipes may call Bash scripts under the relevant
  `scripts/` directory or delegate to nested Makefiles with `$(MAKE) -C ...`, while command logic,
  env loading, shell branching, Docker orchestration, cleanup, and tool invocations belong in
  dedicated scripts such as `backend/scripts/`, `frontend/scripts/`, and `infra/scripts/`.
- Do not change lock files (`backend/uv.lock`, `frontend/package-lock.json`) unless dependencies intentionally changed.
- Do not commit secrets, real tokens, private keys, or `.env` values. Configuration must flow through environment-backed settings.
- Performance and test tooling may import reusable application contracts from `backend/src`, such
  as enums, schemas, factories, and public helpers, but tooling-specific infrastructure must live
  with that tooling. Do not create performance-only or test-only support modules under
  `backend/src`; keep performance support under `backend/performance/` and test support under
  `backend/tests/`.
- UI localisation is backend-bundle driven: user-facing interface strings must come from the
  backend i18n catalog. Database/content localisation is separate from UI i18n: notes, note tags,
  and competency matrix content use required fixed `*_ru` / `*_en` fields in existing tables, with
  explicit `LanguageEnum`/`language` selection for localized read APIs. Competency matrix sheets use
  a stable language-neutral `sheet_key`/`sheetKey`; localized sheet names, sections, subsections,
  questions, answers, expected answers, resource names, and attachment contexts are projections.
  Core note/tag/matrix domain entities keep canonical translation fields only; localized `title`,
  `content`, `folder`, `name`, and matrix text values are response/read-model projections, not
  stored domain-only fields. Do not add generic translation tables, production defaults, or language
  fallbacks unless an explicit design change asks for them. Supported UI languages must be
  represented by an enum, and the initial/default UI language must come from the required
  `I18N_DEFAULT_LANGUAGE` environment setting. Other content localisation remains future work until
  explicitly designed.
- Note analytics must stay privacy-safe unless an explicit design change says otherwise: do not store raw IP addresses, raw user-agent strings, raw referrers, analytics cookies, or third-party analytics identifiers. Referrers may be used only for immediate coarse source classification, and anonymous reactions may store only note-scoped derived identifiers.
- Treat Docker and nginx changes as infrastructure changes: preserve the split where edge nginx routes domains and `/api/*`, while frontend nginx serves the SPA and falls back to `index.html`.
- When Superpowers work is completed, remove task-specific Superpowers markdown artifacts created
  for that work, including finished plans in `docs/superpowers/plans/`, specs/design docs in
  `docs/superpowers/specs/`, and similar temporary `.md` handoff files. Keep only documentation
  that the user explicitly wants to preserve as durable project docs.
- More specific instructions live in nested `AGENTS.md` files under `backend/`, `backend/src/core/`, `backend/src/infra/postgresql/`, `backend/tests/`, `frontend/`, and `frontend/src/app/`.
