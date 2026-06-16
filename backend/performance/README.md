# Performance Testing

This directory contains backend performance tooling for public site behavior and PostgreSQL storage
query plans. Frontend Lighthouse quality and performance gates live under `frontend/lighthouse/`
and run through Lighthouse CI.

## Layout

- `locust/`: HTTP load-test scenario, response validation, and Locust thresholds.
- `query_plans/`: deterministic PostgreSQL seed data, public storage method discovery, real
  SQLAlchemy runtime SQL capture, EXPLAIN runner, thresholds, and report rendering.
- `reports/`: generated Locust and query-plan reports.
- `../scripts/`: shell entrypoints used by Make targets.

## Local Runs

Local Make targets default to `../.env.test`. They prepare backend dependencies, start or reuse the
test PostgreSQL service, start a local backend when `PERFORMANCE_HOST` points to localhost, seed
deterministic public content when `PERFORMANCE_SEED_DATA=true`, and clean up only
services/processes they started. For staging or production-like targets, pass an explicit
`PERFORMANCE_ENV_FILE`.

```bash
make performance-smoke
make performance-baseline
make performance-smoke PERFORMANCE_ENV_FILE=../.env
```

Reports are written to `backend/performance/reports/locust/<timestamp>/` by default:

- `locust-report.html`
- `locust_stats.csv`
- `locust_failures.csv`
- `locust_exceptions.csv`
- `locust_stats_history.csv`
- `backend.log` when the target local backend is started by the performance script

## Lighthouse CI

Use Lighthouse CI from the repository root for lab performance, resource budgets, accessibility,
best-practices, and SEO gates on the Angular hybrid SSR/CSR routes:

```bash
make performance-lighthouse
```

The frontend target builds the production Angular SSR bundle, starts a deterministic mock API and
Node SSR runtime, audits the public case-study, articles list/detail, and matrix list/detail routes,
then writes HTML/JSON reports to `frontend/performance/reports/lighthouse/`.

## Query Plan Checks

Use the query-plan harness when changing PostgreSQL storages, query shapes, seed-sensitive indexes,
or performance thresholds. It starts or reuses the test database, migrates it, clears the
benchmarked tables, seeds a deterministic balanced dataset, discovers every public async
`*DatabaseStorage` method under PostgreSQL storages, runs registered deterministic scenarios for
those methods, captures the SQL actually emitted through SQLAlchemy engine events, then runs:

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON)
```

```bash
make query-plans-balanced
```

The balanced profile seeds 200k articles, 30k tags, 500k article-tag links, 200k competency resources,
representative users, article analytics, reactions, and matrix sheets. Targeted full-text terms are
present in 1% of articles so the measured searches are selective while still running against large
tables. The harness runs `VACUUM ANALYZE` after seeding and before measuring plans.

The gate fails when a discovered public storage method has no scenario, a scenario captures no SQL,
an explained statement exceeds its group or scenario threshold, a configured index is missing, a
forbidden large sequential scan appears, or the plan uses temp blocks. Mutating statements are
explained in rollback-only transactions, and statements from the same storage scenario are replayed
as a group so dependent ORM flush/selectinload/merge SQL remains explainable.

Reports are written to `backend/performance/reports/query-plans/<timestamp>/`:

- `summary.md`
- `summary.json`
- one directory per query with `compiled.sql`, `params.json`, and `explain-run-*.json`

`summary.md` and `summary.json` include storage coverage, scenario-to-method metadata, captured SQL
counts, runtime capture timings, warm median EXPLAIN timings, plan findings, and threshold sources.

## Profiles

- `performance-smoke` is short and suitable for CI. It is meant to catch obvious latency or error regressions, not to establish production capacity.
- `performance-baseline` is longer. With `../.env.test`, it measures the local backend against the
  seeded test database; with staging or production-like targets, pass an explicit
  `PERFORMANCE_ENV_FILE` and set `PERFORMANCE_SEED_DATA=false`.

The checked-in local Locust thresholds are based on a seeded `performance-baseline` run from
2026-06-06 with 15,169 requests, 0 failures, aggregated average 8.9 ms, and aggregated p95 17 ms.
The resulting guard thresholds are `LOCUST_MAX_FAILURE_RATIO=0.0`,
`LOCUST_MAX_AVG_RESPONSE_MS=50`, and `LOCUST_MAX_P95_RESPONSE_MS=75`.

## Useful Environment Values

- `PERFORMANCE_HOST`: target base URL.
- `PERFORMANCE_REPORT_DIR`: report output directory, relative to `backend/` when using Make.
- `PERFORMANCE_LANGUAGE`: UI/content language for localized API calls.
- `PERFORMANCE_INCLUDE_SPA`: set to `true` when the target serves the Angular SPA as well as `/api/*`.
- `PERFORMANCE_INCLUDE_MATRIX_SUGGESTIONS`: set to `true` only for targeted mutation runs that
  should exercise `POST /api/competency-matrix/question-suggestions`; the default test env keeps it
  `false` so smoke/baseline runs remain read-heavy and do not spend the daily suggestion quota.
- `PERFORMANCE_VALIDATE_RESPONSES`: set to `true` to validate selected API responses with backend Pydantic response schemas.
- `PERFORMANCE_SEED_DATA`: set to `true` only for local test-database runs. It seeds published
  articles, article detail content, tags, analytics, reactions, matrix sheets, matrix detail items, and
  resources before Locust starts. The seed runner rejects remote targets, remote databases, and
  database names that do not contain `test`.
- `PERFORMANCE_USERS`, `PERFORMANCE_SPAWN_RATE`, `PERFORMANCE_RUN_TIME`: smoke profile shape.
- `PERFORMANCE_BASELINE_USERS`, `PERFORMANCE_BASELINE_SPAWN_RATE`, `PERFORMANCE_BASELINE_RUN_TIME`: baseline profile shape.
- `LOCUST_MAX_FAILURE_RATIO`, `LOCUST_MAX_AVG_RESPONSE_MS`, `LOCUST_MAX_P95_RESPONSE_MS`: soft-gate thresholds.

## Additional Details

The Make targets prepare the backend uv environment, run Locust, and write timestamped HTML/CSV
artifacts, matching Locust's documented CI and CSV-report workflow. For heavier load, Locust can
run distributed with master/worker processes. Lighthouse CI covers frontend quality and lab
performance gates separately from backend load and SQL-plan checks.

References:

- https://docs.locust.io/en/stable/running-without-web-ui.html
- https://docs.locust.io/en/stable/retrieving-stats.html
- https://docs.locust.io/en/stable/running-distributed.html
- https://web.dev/articles/lighthouse-ci
