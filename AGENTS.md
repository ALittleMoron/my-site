# AGENTS.md

## Project

Portfolio and articles site with a knowledge database

## Stack

- Runtime: Python 3.14, uv, Granian ASGI server
- Framework: Litestar 2.24+
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
- When updating `docs/TODO.md`, do not modify the content or scope of an existing TODO item. Record
  newly discovered follow-up work as a separate TODO item instead of expanding an existing one. Do
  not add the current task to the roadmap merely because it was requested; add only unfinished or
  explicitly requested follow-up work. When an existing TODO item has been fully implemented, change
  its checkbox from `[ ]` to `[x]`; updating completion status is not a content modification and must
  not be skipped.
- For non-trivial tasks, create and follow a structured implementation plan before changing code or
  configuration. Trivial docs-only edits and direct answers do not require a plan.
- If a task turns out to be large enough to risk context degradation, split it into explicit subtasks and run sequential subagents for those subtasks. Each subagent must start its assigned subtask atomically, with a narrow scope and clear handoff back to the main thread.
- Implement behavior changes and bug fixes with TDD by default: add or update the failing test first, then make it pass. If a test is not practical for the change, state why before implementing.
  Do not apply TDD by default to infrastructure-only changes such as Dockerfiles, docker compose,
  nginx, Make targets, deployment scripts, and environment wiring. Add infrastructure tests only
  when there is a high risk of silently regressing a pre-deploy invariant that ordinary checks would
  not catch, such as required environment-variable coverage. Do not add tests that merely assert
  incidental implementation details, such as dependency declarations, package versions, lockfile
  contents, source-code string scans, private helper absence, exact script command text, or the exact
  presence of a Dockerfile command, when a direct review or a real build/run check is the meaningful
  validation.
- Treat UX regressions as real bugs. When changing user-facing flows, check not only correctness but
  also whether the interaction feels stable, predictable, accessible, and respectful of the user's
  context. Bad UX includes theme flashing during navigation or page load, controls that are hard to
  reach or understand, misleading button hierarchy, unclear loading/error states, layout shifts, and
  interfaces that force the user to guess what to do next.
- When adding new functionality that implies access restrictions, ask which user roles should have
  access unless the role policy is already specified. Do not ask this for public/unrestricted
  functionality or when existing instructions already define the role access.
- Every new HTTP handler must be explicitly classified as public, admin, or internal before
  implementation. Public API stays under `/api/*`, admin-panel API stays under `/api/admin/*`, and
  auth/account remain separate cross-cutting contours under `/api/auth/*` and `/api/account/*`.
  Admin UI flows must not reuse public routes when they need privileged data, privileged controls,
  or behavior that may diverge later; duplicate the transport handler instead and keep shared
  schemas/use cases below the HTTP boundary.
- Privileged behavior must be enforced by backend guards and/or use cases, not only by hiding or
  disabling frontend controls. When a UI hides actions based on role or auth state, keep a matching
  backend authorization check and cover the protected path with an API/use-case test.
- Authentication uses explicit `Authorization` bearer access tokens plus a Secure, HttpOnly,
  SameSite session cookie scoped to refresh/logout under `/api/auth/*`. Preserve the required CSRF
  guard header, Fetch Metadata checks, cookie policy, and server-side verification tests. Before
  expanding browser-sent credentials to any additional state-changing handler, design and test the
  matching CSRF boundary in the same backend/frontend change.
- Do not add default values in real production code. API parameters, schemas, dataclasses, settings, helpers, services, and infrastructure-facing code should require callers or environment configuration to pass values explicitly. Filter dataclasses may define defaults for omitted filters, pagination, relationship-loading switches, and list-mode switches when the default means "do not apply this filter" or preserves the normal list behavior; tests, test helpers, and factories may keep defaults when they make test setup clearer.
- Avoid `None`/`null` in production schemas, DTOs, and persisted structured content when a truthful
  non-null representation exists. Prefer empty strings for intentionally blank text, empty
  collections for blank lists, and explicit enum values such as `notSet` for unset finite states.
  Keep `None`/`null` only where absence is semantically necessary or no valid non-null
  representation exists, such as unknown dates, optional filters, external contract fields that are
  explicitly nullable, or framework/browser APIs that naturally return null.
- Before finishing implementation work, do a self-review/code-review pass focused on bugs, regressions, missing tests, and instruction compliance.
- Treat actionable warnings as failures: any warning from project code, tests, tooling, builds, or local runs that can be fixed through project code or configuration, an intentional dependency/runtime/tool update, or another practical fix must be fixed when it first appears. Warnings caused by the current version of a third-party library or its dependencies are not failures when no project-side fix, supported upgrade, or practical alternative exists; in that case, note the warning if relevant and do not derail the current task trying to eliminate it.
- Before claiming completion, run the relevant checks through existing `make` targets: tests, linters, type checks, format checks, migrations, or local-run checks as applicable. For broad or cross-cutting changes, run the full practical check suite. If any relevant check is skipped, explain why in the final response.
- After each code, configuration, documentation, infrastructure, or instruction change, explicitly
  check whether infrastructure, documentation, CI/CD, and relevant `AGENTS.md` instructions must be
  updated; keep them consistent with the change.
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
  - For sufficiently large user-visible, architectural, security, operations, or delivery changes,
    ask whether the change should be added to the public updates/changelog page. Do not ask for
    routine refactoring, small fixes, incidental cleanup, dependency churn, or implementation-only
    details. Prefer grouping related changes under an existing larger milestone, such as auth,
    matrix, deployment, quality, localization, or content workflows, instead of creating a separate
    updates entry for every task.
  - Treat every user correction and every explicit generally applicable instruction as a candidate
    for durable project guidance. At the end of each task, determine whether it is likely to remain
    useful in future sessions.
  - Review the applicable `AGENTS.md` files for accuracy and relevance. Recommend only reusable
    guidance; avoid narrow or task-specific instructions unless they document an important
    exception or materially improve the description of the codebase, its conventions, or the
    correct approach to working with the project.
  - In every final task response, include a separate chat-only `AGENTS.md candidates` section. For
    each candidate, state the concise proposed rule, the exact `AGENTS.md` file where it belongs,
    and why recording it would be useful. If there are no candidates, say so explicitly. Proposals
    may be written in Russian, but content added to an `AGENTS.md` file must be in English. Do not
    write a candidate to any `AGENTS.md` file until the user explicitly approves it.
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
  `make -C backend types`, `make -C backend format-check`, `make -C backend ruff-lint-check`,
  `make -C backend lint-check`, `make -C backend bandit`, `make -C backend security-bandit`,
  `make -C backend security-pip-audit`, `make -C backend vulture`, `make -C backend security`,
  `make performance-smoke`, `make performance-lighthouse`, `make query-plans-realistic`,
  `make query-plans-stress`,
  `make -C frontend test`, `make -C frontend test-coverage`,
  `make -C frontend tests-coverage`, `make -C frontend lint`, `make -C frontend security`,
  `make -C frontend typecheck`, `make -C frontend format-check`, `make -C frontend ssr-smoke`,
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
- Do not commit real or production secrets, tokens, private keys, or environment values.
  Configuration must flow through environment-backed settings. Deterministic non-secret test
  credentials may be committed only in dedicated test fixtures or test environment files and must
  never be usable outside tests.
- UI localisation is backend-bundle driven: user-facing interface strings come from the backend
  i18n catalog, while database/content localisation is selected explicitly through the owning API.
  Read-facing core entities and read models should expose language-neutral projected fields such as
  `title`, `name`, and `content`, populated with the already selected localization instead of
  carrying parallel `*_ru` / `*_en` fields. Write and persistence contracts may keep explicit
  translation fields when both languages are required. Do not add arbitrary language strings,
  implicit fallbacks, or generic translation tables without an explicit design change.
- User-authored Markdown or HTML must render only through the centralized sanitized renderer. Do
  not bind raw authored content to `[innerHTML]`, use `bypassSecurityTrustHtml`, or add a new
  Markdown renderer without XSS regression tests for `<script>`, event-handler attributes, and
  unsafe URL schemes.
- Root Docker Compose and `infra/**` changes must preserve the current private-network and public
  exposure baseline. Do not add public service ports, host networking, privileged containers,
  Docker socket mounts, broad capabilities, or root runtime users unless explicitly required and
  accompanied by a documented security tradeoff. Detailed nginx, CSP, VPN, and edge-routing rules
  belong in `infra/AGENTS.md`.
- Keep agent access as a separate private machine contour. Production transport is only the
  Litestar REST API at `https://agent.<APP_DOMAIN>:18083/internal/agent/v1`, bound to
  `VPN_BIND_ADDRESS` and authenticated by nginx with distinct client certificates. MCP exists only
  as a local stdio bridge. Preserve distinct machine identities, explicit scopes, the closed
  allowlisted REST/tool surface, server-forced Draft behavior, privacy-safe audit, and the isolated
  trusted nginx-to-backend network contour. Never weaken availability with a public/plaintext
  listener, bearer fallback, shared certificate, human PASETO reuse, generic CRUD/HTTP/SQL/shell
  access, publishing, deletion, structure mutation, or server-side URL fetching. Detailed backend
  and edge rules belong in `backend/AGENTS.md`, `infra/AGENTS.md`, and `docs/agent-access.md`.
- More specific instructions live in nested `AGENTS.md` files under `infra/`, `backend/`,
  `backend/src/core/`, `backend/src/infra/postgresql/`, `backend/tests/`, `frontend/`,
  `frontend/src/app/`, `frontend/src/app/core/editor/`, and
  `frontend/src/app/features/admin-panel/`.
