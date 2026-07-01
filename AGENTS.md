# AGENTS.md

## Project

Portfolio and articles site with a knowledge database

## Stack

- Runtime: Python 3.14, uv, Granian ASGI server
- Framework: Litestar 2.23+
- DB: PostgreSQL 18.4 + SQLAlchemy 2.0 async + Alembic
- DI: Dishka
- Cache: Valkey
- Background tasks: TaskIQ + taskiq-redis over Valkey
- File storage: MinIO through an aiobotocore S3-compatible adapter
- Auth: PASETO (pyseto) + Argon2 password hashing
- Logging: structlog + ECS logging + Sentry SDK
- Frontend: Angular 22 hybrid SSR/CSR + Bootstrap 5, served by a frontend-owned Node.js SSR image
- Edge: nginx reverse proxy for TLS, `/api/*`, exact `/sitemap.xml` and `/robots.txt`, frontend, the public MinIO object endpoint, and VPN-only internal web panel routing

## General rules

- When library/API documentation, code generation, setup, or configuration steps are needed, search the internet without me having to explicitly ask. Prefer official documentation and primary sources, and cite the sources used in the response.
- Do not perform any git action that changes repository state unless I explicitly ask for it. This includes `git add`, `git commit`, `git push`, `git stash`, branch creation, branch switching, rebasing, merging, resetting, checking out files, and similar mutating operations.
- The site has not been deployed yet. For unpublished contracts, routes, database schemas, and
  content syntax, prefer clean changes over compatibility layers, redirects, aliases, or migration
  detours unless an explicit design asks for backward compatibility.
- For non-trivial tasks, create and follow a Superpowers implementation plan before changing code or configuration. Trivial docs-only edits and direct answers do not require a plan.
- If a task turns out to be large enough to risk context degradation, split it into explicit subtasks and run sequential subagents for those subtasks. Each subagent must start its assigned subtask atomically, with a narrow scope and clear handoff back to the main thread.
- Implement behavior changes and bug fixes with TDD by default: add or update the failing test first, then make it pass. If a test is not practical for the change, state why before implementing.
  Do not apply TDD by default to infrastructure-only changes such as Dockerfiles, docker compose,
  nginx, Make targets, deployment scripts, and environment wiring. Add infrastructure tests only
  when there is a high risk of silently regressing a pre-deploy invariant that ordinary checks would
  not catch, such as required environment-variable coverage. Do not add tests that merely assert
  incidental implementation details, such as the exact presence of a Dockerfile command, when a
  direct review or a real build/run check is the meaningful validation.
- Treat UX regressions as real bugs. When changing user-facing flows, check not only correctness but
  also whether the interaction feels stable, predictable, accessible, and respectful of the user's
  context. Bad UX includes theme flashing during navigation or page load, controls that are hard to
  reach or understand, misleading button hierarchy, unclear loading/error states, layout shifts, and
  interfaces that force the user to guess what to do next.
- When adding new functionality that implies access restrictions, ask which user roles should have
  access unless the role policy is already specified. Do not ask this for public/unrestricted
  functionality or when existing instructions already define the role access.
- Every new HTTP handler must be explicitly classified as public, admin, or future internal before
  implementation. Public API stays under `/api/*`, admin-panel API stays under `/api/admin/*`, and
  auth/account remain separate cross-cutting contours under `/api/auth/*` and `/api/account/*`.
  Admin UI flows must not reuse public routes when they need privileged data, privileged controls,
  or behavior that may diverge later; duplicate the transport handler instead and keep shared
  schemas/use cases below the HTTP boundary.
- Do not add default values in real production code. API parameters, schemas, dataclasses, settings, helpers, services, and infrastructure-facing code should require callers or environment configuration to pass values explicitly. Filter dataclasses may define defaults for omitted filters, pagination, relationship-loading switches, and list-mode switches when the default means "do not apply this filter" or preserves the normal list behavior; tests, test helpers, and factories may keep defaults when they make test setup clearer.
- Avoid `None`/`null` in production schemas, DTOs, and persisted structured content when a truthful
  non-null representation exists. Prefer empty strings for intentionally blank text, empty
  collections for blank lists, and explicit enum values such as `notSet` for unset finite states.
  Keep `None`/`null` only where absence is semantically necessary or no valid non-null
  representation exists, such as unknown dates, optional filters, external contract fields that are
  explicitly nullable, or framework/browser APIs that naturally return null.
- Before finishing implementation work, do a self-review/code-review pass focused on bugs, regressions, missing tests, and instruction compliance.
- Treat warnings as failures: any warning from project code, tests, tooling, builds, or local runs is a real problem and must be fixed when it first appears. The only exception is a warning that originates inside a third-party library dependency and still cannot be fixed after updating the relevant library to its latest available version.
- Before claiming completion, run the relevant checks through existing `make` targets: tests, linters, type checks, format checks, migrations, or local-run checks as applicable. For broad or cross-cutting changes, run the full practical check suite. If any relevant check is skipped, explain why in the final response.
- After each code or configuration change, explicitly check whether infrastructure, documentation, CI/CD, and relevant `AGENTS.md` instructions must be updated; keep them consistent with the change.
  - At minimum, search related terms in `docs/`, `.github/`, root README-style files, and nested `AGENTS.md` files before finishing.
  - After changes in code, architecture, implementation approach, accepted engineering decisions,
    quality/security/operations posture, roadmap, or "what next" direction, explicitly analyze
    whether the public "How this site is built" case-study page (`/ru/how-this-site-is-built`,
    `/en/how-this-site-is-built`) should be updated. Decide what should be added, removed, or
    changed there, and keep that page current when the change affects the site's public technical
    story.
  - Do not present trivial implementation facts, routine CRUD, ordinary normalized database
    modeling, framework defaults, or other baseline engineering hygiene as "technology choices" or
    public case-study highlights. The case-study page should mention only decisions that are
    genuinely distinctive, risky, educational, or important to the product's architecture,
    security, operations, UX, or quality story.
  - After every code, configuration, documentation, infrastructure, or instruction change, explicitly ask whether the change should be captured in the relevant `AGENTS.md`. Do not silently decide that `AGENTS.md` does not need an update.
  - If no documentation, infrastructure, CI/CD, or instruction updates are needed, mention that check in the final response.
- Use existing `make` targets for installation, checks, tests, migrations, and local runs when available instead of calling lower-level tools directly.
- Never bypass Make targets for tests or checks. Test, lint, type-check, security, format-check,
  coverage, quality, build-verification, and similar validation commands must be run only through
  existing `make` targets. Do not call lower-level tools such as `pytest`, `ruff`, `mypy`,
  `coverage`, `bandit`, `vulture`, `npm`, or framework CLIs directly unless I explicitly instruct
  that exact bypass for the current task. If a Make target cannot run because of local environment
  or permission issues, report the blocker instead of bypassing Make.
- The following Make commands are trusted for agent use and may be approved as recurring command
  prefixes when the local Codex permission flow asks for them:
  `make test-backend-unit`, `make test-backend`, `make test-backend-integration`,
  `make test-frontend`, `make tests`, `make tests-fast`, `make tests-coverage`,
  `make tests-coverage-frontend`, `make -C backend test-unit`, `make -C backend test`,
  `make -C backend test-integration`, `make -C backend tests-coverage`,
  `make -C backend types`, `make -C backend lint-check`, `make -C backend bandit`,
  `make -C backend vulture`, `make -C backend security`, `make -C frontend test`,
  `make -C frontend test-coverage`, `make -C frontend tests-coverage`,
  `make -C frontend lint`, `make -C frontend typecheck`, `make -C frontend format-check`,
  and `make -C frontend build`.
- Before adding any new Make command to the trusted-for-agents list, inspect the target and the
  scripts it delegates to for agent-safety risks, including repository writes, destructive file or
  Docker operations, database migrations or downgrades, dependency installation, network access,
  secret exposure, long-running services, and other broad side effects.
- Check, test, coverage, quality, query-plan, and performance Make targets must be self-contained:
  they should conditionally prepare dependencies, load the required test environment, start required
  test services or local backend processes, prepare deterministic data where applicable, and clean
  up only resources they started themselves.
- Keep Makefiles as thin wrappers only: Make recipes may call Bash scripts under the relevant
  `scripts/` directory or delegate to nested Makefiles with `$(MAKE) -C ...`, while command logic,
  env loading, shell branching, Docker orchestration, cleanup, and tool invocations belong in
  dedicated scripts such as `backend/scripts/`, `frontend/scripts/`, and `infra/scripts/`.
- Do not change lock files (`backend/uv.lock`, `frontend/package-lock.json`) unless dependencies intentionally changed.
- When changing any library, dependency, runtime, or tool version, update the matching badges in `.github/badges/` in the same change.
- Frontend npm installs must enforce peer dependency contracts. Resolve Angular, TypeScript, and tooling peer dependency conflicts in `frontend/package.json` and `frontend/package-lock.json` instead of using `--legacy-peer-deps` or `--force`, except for an explicitly documented temporary workaround with a TODO and removal plan.
- Do not commit secrets, real tokens, private keys, or `.env` values. Configuration must flow through environment-backed settings.
- Performance and test tooling may import reusable application contracts from `backend/src`, such
  as enums, schemas, factories, and public helpers, but tooling-specific infrastructure must live
  with that tooling. Do not create performance-only or test-only support modules under
  `backend/src`; keep performance support under `backend/performance/` and test support under
  `backend/tests/`.
- UI localisation is backend-bundle driven: user-facing interface strings must come from the
  backend i18n catalog. Database/content localisation is separate from UI i18n: articles, article tags,
  and competency matrix content use required fixed `*_ru` / `*_en` fields in their owning tables, with
  explicit `LanguageEnum`/`language` selection for localized read APIs. Competency matrix
  sheet/section/subsection names live in normalized structure tables, questions store required
  `subsection_id`, and sheets use a stable language-neutral `key`/`sheetKey`; localized sheet names,
  sections, subsections, questions, answers, expected answers, resource names, and attachment
  contexts are projections.
  Resumes are single-language structured documents: store required `LanguageEnum`/`language` on the
  resume, keep one content shape without resume-specific `*_ru` / `*_en` fields, and do not validate
  whether the authored text actually matches the selected language.
  Core article/tag/matrix domain entities keep canonical translation fields only; localized `title`,
  `content`, `folder`, `name`, and matrix text values are response/read-model projections, not
  stored domain-only fields. Do not add generic translation tables, production defaults, or language
  fallbacks unless an explicit design change asks for them. Supported UI languages must be
  represented by an enum, and the initial/default UI language must come from the required
  `I18N_DEFAULT_LANGUAGE` environment setting. Other content localisation beyond articles, article
  tags, competency matrix content, and resumes remains future work until explicitly designed.
- Articles are the authored content model. SEO metadata for articles is explicit and
  nullable: API write payloads must include a
  `metadata` object, but `seo_title_ru`, `seo_title_en`, `seo_description_ru`,
  `seo_description_en`, `cover_image_url`, `cover_image_alt_ru`, and `cover_image_alt_en` may be
  null. SEO analysis is advisory-only and must not block saving or publishing. Wiki-style content
  links use typed prefixes, currently `[[articles:<slug>]]` and `[[matrix:<slug>]]`, with optional
  labels such as `[[matrix:<slug>|Custom label]]`; unprefixed `[[article-slug]]` syntax is not
  supported.
- Article analytics must stay privacy-safe unless an explicit design change says otherwise: do not store raw IP addresses, raw user-agent strings, raw referrers, analytics cookies, or third-party analytics identifiers. Referrers may be used only for immediate coarse source classification, and anonymous reactions may store only article-scoped derived identifiers.
- Treat Docker and nginx changes as infrastructure changes: preserve the split where edge nginx routes public domains, `/api/*`, `/sitemap.xml`, `/robots.txt`, and the public MinIO object endpoint, while VPN-only internal web panels remain bound to `VPN_BIND_ADDRESS` and the frontend container runs the Angular Node.js SSR runtime for public article, site-build case-study, and matrix question routes and hydrates interactive CSR/content-authoring areas.
- Coarse public request rate limiting for the current security baseline belongs to edge nginx, not
  backend application middleware. Do not add backend/Litestar rate limiting unless an explicit
  identity-aware or business-quota design requires application-level limits by user, account, API
  key, tenant, or subscription plan.
- When Superpowers work is completed, remove task-specific Superpowers markdown artifacts created
  for that work, including finished plans in `docs/superpowers/plans/`, specs/design docs in
  `docs/superpowers/specs/`, and similar temporary `.md` handoff files. Keep only documentation
  that the user explicitly wants to preserve as durable project docs.
- More specific instructions live in nested `AGENTS.md` files under `backend/`, `backend/src/core/`, `backend/src/infra/postgresql/`, `backend/tests/`, `frontend/`, and `frontend/src/app/`.
