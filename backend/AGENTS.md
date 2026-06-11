# Backend Instructions

Unless a section states a broader scope, these rules apply to backend Python code under
`backend/**/*.py`.

## Code Style

- line-length: 100 (ruff + black)
- ruff: ALL rules, see ignores in `pyproject.toml`
- mypy: strict mode (`disallow_untyped_defs = true` etc.)
- No docstrings unless interface is non-obvious from types
- Comments: only for non-obvious WHY, never WHAT
- Keep reusable backend tuning values, parser rules, supported formats, limits, headers, and other
  code-owned constants in `backend/src/infra/config/constants.py`; do not create feature-specific
  constants modules or module-local constants for those values in services, storages, parsers, or
  adapters. Core code must receive such values through schemas/constructor parameters or IOC
  wiring, while infra and entrypoint code may import `constants` directly when that layer owns the
  wiring.

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
- When an existing use-case operation already represents the business action, reuse it with
  explicit parameters that model transport/auth/quota differences instead of adding a parallel
  use-case method for the same action. Do not use sentinel values such as arbitrarily large quotas;
  make the variation explicit in the parameter contract.
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
- Put reusable domain parsers in the domain `parsers.py`, reader interfaces in `readers.py`,
  parser/request DTOs and rule objects in `schemas.py`, and parser/domain errors in
  `exceptions.py`. Do not name domain files after one narrow feature when an existing standard
  file type fits the object.
- Top-level functions are acceptable when the framework or tool naturally requires them or when a
  callable class would add ceremony without improving ownership: app factories, Litestar lifespan
  hooks, CLI commands, Alembic migration functions, and small pure infrastructure entrypoints.
- When choosing between a function and a method, prefer the shape that expresses real ownership.
  Do not move code into a class solely to satisfy a stylistic ban on functions.
- Prefer moving meaningful multi-parameter object creation into methods on the object that owns
  that creation logic, or into the owning use case when the object is an aggregate/read model.
  Do not extract creation solely for tiny objects with too few fields to justify the extra method.
- Aggregating core objects such as note lists, note trees, analytics summaries, and similar
  use-case-shaped read models must be assembled in core use cases or on the owning core object.
  Storage adapters must return persisted entities or narrow row/data objects needed for assembly;
  they must not collect, group, paginate, or summarize those rows into complex core aggregates.
  Simple one-field containers such as `Tags(values=...)` and `ExternalResources(values=...)`
  may remain at storage boundaries when they only wrap loaded values.

## HTTP and Schemas

- API controllers must contain only HTTP validation, auth/permission checks, use case calls, and request/response mapping.
- Controllers must receive dependencies through `FromDishka[...]`, preferably typed as abstract use case interfaces.
- Endpoint/controller modules must not define `@staticmethod`, `@classmethod`, or private helper
  methods for request-derived values or parameter assembly when a Litestar `Provide` dependency can
  own that logic. Put those dependencies in a neighboring `dependencies.py` module.
- When an endpoint receives many query, path, header, or cookie parameters and only assembles them
  into one filter/read parameter object, prefer moving that assembly into a Litestar `Provide`
  dependency in a neighboring `dependencies.py` module so the handler receives the object directly.
- Public discovery response assembly, such as sitemap URL collection, sitemap XML rendering, and
  robots.txt rendering, must not live in `endpoints.py` controller modules. Keep it in a neighboring
  `backend/src/entrypoints/litestar/**` module owned by the HTTP entrypoint layer, not in `core`.
- API schemas must inherit from the shared schema bases and explicitly map to/from domain objects with `to_schema` / `from_domain_schema`.
- Use `to_domain_schema` / `from_domain_schema` for same-concept conversions between API schemas, ORM models, and core domain schemas when the method signature already identifies the exact source/target type. Use a more specific conversion method name only when the conversion changes the semantic entity, such as attached resource -> plain external resource.
- Do not pass Pydantic API schemas, SQLAlchemy models, or Litestar types into the core layer.

## Response Caching

- Cache API GET responses only through the domain response cache helpers in
  `backend/src/entrypoints/litestar/response_cache.py`. Use a `ResponseCacheDomain`
  and its `cache_key_builder` property so keys are domain-prefixed and routed to the
  matching Valkey namespace; do not add ad hoc cache key builders or write directly to a
  shared response-cache namespace.
- Safe, stable GET handlers may use Litestar response caching with explicit cache metadata.
  Keep user-implicit, privileged statistics, analytics, presign URL, account/session, and other
  request-side-effect or user-specific responses uncached unless a new design explicitly
  makes their cache key and invalidation rules safe.
- If a cached GET depends on auth-sensitive query parameters, enforce the access check with a
  Litestar guard or another pre-cache boundary check. Do not rely only on controller body checks
  because Litestar can return a cached response before executing the handler body.
- Mutating handlers that change cached domain content must call
  `invalidate_response_cache_domain(...)` only after the use case succeeds. Do not invalidate on
  validation/auth failures, and do not invalidate content caches for analytics-only changes when
  analytics are served from separate uncached endpoints.

## I18n

- The backend i18n catalog is the source of truth for UI interface strings and enum labels.
  Database/content localisation is separate from the UI catalog.
- Notes, note tags, and competency matrix content localise with required fixed fields in existing tables:
  `title_ru`, `title_en`, `content_ru`, `content_en`, `folder_ru`, `folder_en`, `name_ru`,
  `name_en`, plus competency matrix `question_*`, `answer_*`, `interview_expected_answer_*`,
  `sheet_*`, `section_*`, `subsection_*`, resource `name_*`, and attachment `context_*` fields.
  Competency matrix sheets must use a stable language-neutral `sheet_key`/`sheetKey` identifier.
  Do not add generic translation tables, production defaults, or fallback language behavior unless
  an explicit design change asks for them.
- Core note, tag, and competency matrix domain entities must not store localized projection fields
  such as `title`, `content`, `folder`, `name`, or localized matrix text. Keep canonical RU/EN
  fields on the domain object and build localized public values in response schemas or explicit read
  models using `LanguageEnum`.
- Note article SEO metadata belongs to the note contract, not to a generic translation table.
  Keep the explicit nullable fields `seo_title_ru`, `seo_title_en`, `seo_description_ru`,
  `seo_description_en`, `cover_image_url`, `cover_image_alt_ru`, and `cover_image_alt_en` on note
  domain/API/storage models. Note create/update API payloads must require the `metadata` object
  itself while allowing individual metadata fields to be null, with no production defaults.
- Read/write APIs that expose localized note, tag, or competency matrix content must use the
  backend language enum and require explicit `LanguageEnum`/`language` selection where localized
  values are returned.
- Supported UI languages must be modeled with a backend enum. Do not accept arbitrary language
  strings in production API/settings code.
- The default UI language must be configured explicitly through the required
  `I18N_DEFAULT_LANGUAGE` environment setting; do not add production defaults for it.
- Keep the available-languages endpoint and bundle endpoint consistent with the enum and catalog,
  and cover new languages/keys with catalog parity tests.
- Non-note and non-matrix content localisation remains future work until explicitly designed.

## Persistence

- SQLAlchemy models and database storages live only under `backend/src/infra/postgresql/`.
- Database storages return domain schemas, not ORM models.
- Storages may `flush`, but must not `commit`; transaction ownership belongs to the DI/session provider.
- Every DB model change must include a matching Alembic migration.

## Performance

- For backend changes that can realistically affect runtime performance, run
  `make performance-smoke` before the first implementation change and again after the task, then
  compare the generated reports to check for regressions. This applies to query shape, storage
  access patterns, API handlers/use cases, serialization, caching, external I/O, migrations, or
  data-volume behavior.
- Skip this before/after smoke workflow for small edits with no credible performance impact, such
  as narrow documentation, formatting, test-only, typing-only, naming-only, or localized mechanical
  changes. If a pre-change smoke cannot be run because the task starts from a broken state, record
  that in the final response and compare against the nearest available baseline/report instead.

## Dependency Injection

- Dishka providers are wiring only: no business logic, DB queries, or external side effects.
- Use `Scope.APP` only for stateless singleton-safe dependencies; use `Scope.REQUEST` for sessions, storages, and use cases.
