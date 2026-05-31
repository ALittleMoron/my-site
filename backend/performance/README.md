# Performance Testing

This directory contains the first CI-safe Locust profile for public site behavior.

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
