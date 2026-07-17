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
benchmarked tables, seeds a deterministic selected-profile dataset, discovers every public async
`*DatabaseStorage` method under PostgreSQL storages, runs registered deterministic scenarios for
those methods, captures the SQL actually emitted through SQLAlchemy engine events, then runs:

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON)
```

```bash
make query-plans-realistic
make query-plans-stress
```

`realistic` is the required regression gate on `main`; `stress` is a manual capacity diagnostic.
Both use three EXPLAIN runs, keep about 80% of articles published, and place deterministic full-text
matches in 1% of articles. Every matching article is published. The harness runs `VACUUM ANALYZE`
after seeding and before measuring plans.

The EXPLAIN session uses an explicit `work_mem` budget (`16MB` for `realistic`, `64MB` for
`stress`) so temp-block findings are reproducible instead of depending on the PostgreSQL host
default. Any temp read or write block remains blocking after that profile budget is applied.

Local `stress` runs start an isolated disk-backed PostgreSQL container on port `55433` by default
and remove it on exit; this avoids the intentionally RAM-backed general test database running out
of space. Override that port with `QUERY_PLANS_STRESS_DB_PORT`. GitHub Actions reuses its dedicated
job service instead. `realistic` continues to start or reuse the normal test database.

| Domain volumes | `realistic` | `stress` |
|---|---:|---:|
| Users / auth sessions | 100 / 500 | 10k / 50k |
| Article folders / articles | 20 / 5k | 200 / 200k |
| Tags / article-tag links | 500 / 20k | 30k / 500k |
| Daily analytics / reactions | 100k / 10k | 2m / 500k |
| Resumes | 250 | 50k |
| Matrix items / resources / links | 10k / 5k / 25k | 200k / 200k / 500k |
| Queued questions / Agent audit events | 5k / 10k | 50k / 250k |
| Matrix sheets × sections × subsections | 20 × 8 × 12 | 20 × 8 × 12 |

The gate fails when a discovered public storage method has no scenario, a scenario captures no SQL,
or the plan uses temp blocks. Missing configured indexes and forbidden sequential scans block at
relation cardinalities of 1,000 rows or more and are observations below that boundary. `realistic`
also blocks on its absolute latency SLA; `stress` reports SLA overruns as observations while keeping
plan-shape and temp-block checks strict. Mutating statements are explained in rollback-only
transactions, and statements from the same storage scenario are replayed as a group so dependent
ORM flush/selectinload/merge SQL remains explainable.

The absolute query-group ceilings remain 25/250/150/250/100/300 ms. Until a calibrated baseline is
committed, `realistic` uses those ceilings directly. To prepare the relative gate, download exactly
five `realistic` `summary.json` artifacts produced from the same GitHub SHA, then run:

```bash
make query-plans-baseline-candidate \
  QUERY_PLAN_BASELINE_SOURCE_SHA=<sha> \
  QUERY_PLAN_BASELINE_OUTPUT=performance/query_plans/realistic-baseline.json \
  QUERY_PLAN_BASELINE_SUMMARY_1=/tmp/run-1/summary.json \
  QUERY_PLAN_BASELINE_SUMMARY_2=/tmp/run-2/summary.json \
  QUERY_PLAN_BASELINE_SUMMARY_3=/tmp/run-3/summary.json \
  QUERY_PLAN_BASELINE_SUMMARY_4=/tmp/run-4/summary.json \
  QUERY_PLAN_BASELINE_SUMMARY_5=/tmp/run-5/summary.json
```

The candidate generator rejects non-`realistic` samples, any sample count other than five, and
different query sets. It stores profile, source SHA, sample count, and the median of the five warm
medians for each query. Once committed, the effective `realistic` threshold becomes
`min(SLA, max(2 × baseline, baseline + 20 ms))`; missing or stale query names then fail the run.

Reports are written to `backend/performance/reports/query-plans/<timestamp>/`:

- `summary.md`
- `summary.json`
- one directory per query with `compiled.sql`, `params.json`, and `explain-run-*.json`

`summary.md` and `summary.json` include the full relation-cardinality map, timing mode, storage
coverage, scenario-to-method metadata, captured SQL counts, warm median EXPLAIN timings, SLA,
baseline, effective threshold, overrun flag, and separate blocking findings and observations.

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
  resources before Locust starts. Seeded slugs and matrix sheet keys use the `perf-seed-*` prefix so
  local runs can coexist with other test datasets; seeded matrix discovery is restricted to that
  prefix so unrelated query-plan or developer data cannot distort the load profile. The seed runner
  rejects remote targets, remote databases, and database names that do not contain `test`.
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
