# Backend Testing Instructions

These rules apply to backend tests under `backend/tests/**/*.py`.

## Philosophy

TDD. Tests drive implementation. Unit tests cover all logic branches. Integration tests cover success paths only.

## Unit vs. Integration Tests

| Type | Definition | Directory |
|---|---|---|
| Unit | Single layer in isolation. Uses mock storages/providers. | `backend/tests/unit/` |
| Integration | DB storages + core together, no mocks. Happy path only. | `backend/tests/integration/` |
| Migration | Alembic revision upgrade/downgrade behavior against real PostgreSQL. | `backend/tests/migrations/` |

## Unit Tests

- Test a single layer in isolation. Any directory can have unit tests.
- No real DB, no real external services.
- Mock storages via `Mock(spec=SomeStorageABC)`.
- Test every branch: happy path, validation errors, domain exceptions.
- Inherit `TestCase` for `self.factory.core.*` / `self.factory.api.*`.

## Integration Tests

- Test the full stack: HTTP -> handler -> use case -> real DB (no mocks anywhere).
- Happy path only.
- Real PostgreSQL test DB (`my_site_database_test`) — tests under `backend/tests/integration/`
  are auto-migrated to `heads` via their package conftest.
- Real Dishka providers (not mocks).
- Inherit `StorageTestCase` for DB assertion helpers; session auto-rollbacks after each test.
- Alembic migration tests live outside `integration/` under `backend/tests/migrations/`, with one
  file per revision such as `test_0001.py`; each file should cover upgrade and downgrade behavior
  and explicitly call migration helpers for the revision under test.

## Migration Tests

- Prefer testing migrations against populated tables affected by the revision. For a migration that
  changes an existing table, migrate to the revision immediately before the one under test, insert
  representative rows into that table, then run the target migration and assert the data/schema
  result.
- Do not import application ORM models in migration tests. Use only SQLAlchemy Core tables,
  columns, expressions, and query builder constructs because later revisions may remove or reshape
  ORM models that older migration tests still need to exercise.
- Raw SQL is prohibited completely in migration tests: do not use handwritten SQL strings,
  `sqlalchemy.text()`, `op.execute()` with SQL strings, or `connection.exec_driver_sql()`.

## Commands

```bash
make test-unit           # unit tests only (fast, run often)
make test-integration    # integration + migration tests; starts/reuses test DB automatically
make tests               # all tests
make tests-coverage      # all + coverage report
```

From the repository root:

```bash
make tests-fast          # backend unit + frontend tests; no backend test PostgreSQL
make tests-compose       # starts/reuses test PostgreSQL, runs tests, then cleans up owned services
make test-env-up         # start isolated test PostgreSQL manually
make test-env-down       # stop isolated test PostgreSQL and remove its data
```

Backend pytest parallelism is explicit. Do not use `pytest-xdist -n auto`: the Make-backed test
script computes physical CPU cores and passes `-n <workers>` itself. Override it only with
`BACKEND_PYTEST_WORKERS`: `0` and `1` force serial execution, while any value greater than `1`
forces that exact worker count.

`make test-unit` runs only `backend/tests/unit/` and must not require a test database. Integration
pytest workers clone a migrated run-scoped template database into isolated PostgreSQL databases
named from the base database plus the xdist worker suffix, such as `my_site_database_test_gw0`.
Alembic migration tests must stay serial because they exercise upgrade/downgrade behavior against
the shared base schema.

## Patterns

- Shared test cases: `backend/tests/test_cases.py` — `TestCase`, `ContainerTestCase`,
  `ApiTestCase`, `StorageTestCase`
- Mock providers for unit tests: `backend/tests/unit/mocks/providers/`
- Test data factories in `backend/tests/helpers/factories/`: `CoreFactoryHelper` (domain objects), `ApiFactoryHelper` (request payloads) — plain Python, no Mimesis
- Access common helpers via `self.factory.*`, `self.asserts.*`, and `self.collections.*` —
  inherit from `TestCase` or a more specific test case class.
- Defaults are allowed in tests, test helpers, and factories when they reduce noise and make the required fields for a scenario easier to see.
- Unit test mocking: `Mock(spec=SomeStorageABC)` from `unittest.mock`
- Unit tests that need only factories/assertions/collections: inherit `TestCase`.
- Unit tests that need the Dishka test container but not HTTP helpers: inherit `ContainerTestCase`.
- API tests: inherit `ApiTestCase` -> `self.api.*` / `self.no_auth_api.*`, DI container helpers,
  factories, assertions, and collection helpers.
- Integration DB tests: inherit `StorageTestCase` -> `self.storage_helper.*`, session
  auto-rollbacks, factories, assertions, and collection helpers.
- Add API helper methods in `backend/tests/helpers/api.py` instead of duplicating endpoint URL strings across tests.
- Put shared HTTP assertion methods in `AssertsHelper` under
  `backend/tests/helpers/assertions.py`; call them as `self.asserts.status(...)`,
  `self.asserts.error_message(...)`, `self.asserts.json_body(...)`, or
  `self.asserts.resume_response_contract(...)`. Keep scenario-specific payload assertions visible
  in the test body. When a test needs to inspect a response JSON body after checking only status,
  call `self.asserts.status(...)` first and then `response.json()` directly.
- Put small collection projection methods in `CollectionsHelper` under
  `backend/tests/helpers/collections.py`; call them as `self.collections.slugs(items)`,
  `self.collections.ids(items)`, or `self.collections.names_en(items)` when that is clearer than a
  repeated comprehension.
- Create domain test objects through `self.factory.core.*`; direct dataclass construction is only for cases not covered by factories yet.
- Add reusable domain builders to `CoreFactoryHelper` when the same multi-object setup appears in
  API, core, and integration tests; keep scenario-only data local to the test.
- Unit API tests verify HTTP contract and use case calls. Unit core tests verify branch logic. Storage behavior belongs in integration tests.
- Cover DB/storage changes with integration tests through `StorageTestCase`.
- Do not add tests that only mirror ORM metadata/index declarations or trivial one-to-one model
  converters. They do not validate behavior; cover storage behavior through integration tests
  instead.
- Do not add tests that pin dependency declarations, package versions, lockfile contents,
  pyproject/package metadata, exact shell command strings, source-code text, private helper absence,
  or other implementation trivia. If a high-risk invariant deserves automation, test the observable
  behavior, generated schema, security boundary, migration/data result, query-plan coverage, or a
  real Make-backed smoke path instead.

## Coverage Target

95% — driven by unit tests and database integration tests.

Core layer should be 100% coverage.

## Test File Naming

`test_<action>_<expected_result>.py` — e.g. `test_create_item_returns_201.py`, `test_create_item_rejects_empty_title.py`
