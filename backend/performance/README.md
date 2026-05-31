# Performance Testing

This directory contains performance tooling for public site behavior and PostgreSQL search query
plans.

## Layout

- `locust/`: HTTP load-test scenario, response validation, and Locust thresholds.
- `query_plans/`: deterministic PostgreSQL seed data, real SQLAlchemy query capture, compiled SQL
  output, EXPLAIN runner, and report rendering.
- `reports/`: generated Locust and query-plan reports.
- `../scripts/`: shell entrypoints used by Make targets.

## Local Runs

Create `.env` from `.env.example`, then tune the `PERFORMANCE_*` and `LOCUST_MAX_*`
values there.

```bash
make install-performance
make performance-smoke
make performance-baseline
```

Reports are written to `backend/performance/reports/` by default:

- `locust-report.html`
- `locust_stats.csv`
- `locust_failures.csv`
- `locust_exceptions.csv`
- `locust_stats_history.csv`

## Query Plan Checks

Use the query-plan harness when changing search queries or PostgreSQL indexes. It runs against the
test database only by default, migrates it, clears the benchmarked tables, seeds a deterministic
balanced dataset, compiles the real SQLAlchemy storage queries, then runs:

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON)
```

```bash
make test-env-up
make query-plans-balanced
make test-env-down
```

The balanced profile seeds 200k notes, 30k tags, 500k note-tag links, and 200k competency resources.
Targeted full-text terms are present in 1% of notes so the measured searches are selective while
still running against large tables. The harness runs `VACUUM ANALYZE` after seeding and before
measuring plans.

Reports are written to `backend/performance/reports/query-plans/`:

- `summary.md`
- `summary.json`
- one directory per query with `compiled.sql`, `params.json`, and `explain-run-*.json`

## Profiles

- `performance-smoke` is short and suitable for CI. It is meant to catch obvious latency or error regressions, not to establish production capacity.
- `performance-baseline` is longer and should run against staging or a production-like environment.

## Useful Environment Values

- `PERFORMANCE_HOST`: target base URL.
- `PERFORMANCE_REPORT_DIR`: report output directory, relative to `backend/` when using Make.
- `PERFORMANCE_LANGUAGE`: UI/content language for localized API calls.
- `PERFORMANCE_INCLUDE_SPA`: set to `true` when the target serves the Angular SPA as well as `/api/*`.
- `PERFORMANCE_VALIDATE_RESPONSES`: set to `true` to validate selected API responses with backend Pydantic response schemas.
- `PERFORMANCE_USERS`, `PERFORMANCE_SPAWN_RATE`, `PERFORMANCE_RUN_TIME`: smoke profile shape.
- `PERFORMANCE_BASELINE_USERS`, `PERFORMANCE_BASELINE_SPAWN_RATE`, `PERFORMANCE_BASELINE_RUN_TIME`: baseline profile shape.
- `LOCUST_MAX_FAILURE_RATIO`, `LOCUST_MAX_AVG_RESPONSE_MS`, `LOCUST_MAX_P95_RESPONSE_MS`: soft-gate thresholds.

## Notes

The Make targets run Locust from the backend uv environment and write HTML/CSV artifacts, matching Locust's documented CI and CSV-report workflow. For heavier load, Locust can run distributed with master/worker processes. Lighthouse CI is still tracked separately for frontend lab metrics and budgets.

References:

- https://docs.locust.io/en/stable/running-without-web-ui.html
- https://docs.locust.io/en/stable/retrieving-stats.html
- https://docs.locust.io/en/stable/running-distributed.html
- https://web.dev/articles/lighthouse-ci
