# Backend Testing Instructions

These rules apply to backend tests under `backend/tests/**/*.py`.

## Philosophy

TDD. Tests drive implementation. Unit tests cover all logic branches. Integration tests cover success paths only.

## Unit vs. Integration Tests

| Type | Definition | Directory |
|---|---|---|
| Unit | Single layer in isolation. Uses mock storages/providers. | `backend/tests/unit/` |
| Integration | DB storages + core together, no mocks. Happy path only. | `backend/tests/integration/` |

## Unit Tests

- Test a single layer in isolation. Any directory can have unit tests.
- No real DB, no real external services.
- Mock storages via `Mock(spec=SomeStorageABC)`.
- Test every branch: happy path, validation errors, domain exceptions.
- Inherit `FactoryFixture` for `self.factory.core.*` / `self.factory.api.*`.

## Integration Tests

- Test the full stack: HTTP -> handler -> use case -> real DB (no mocks anywhere).
- Happy path only.
- Real PostgreSQL test DB (`my_site_database_test`) — auto-migrated via conftest.
- Real Dishka providers (not mocks).
- Inherit `StorageFixture` for DB assertion helpers; session auto-rollbacks after each test.

## Commands

```bash
make test-unit           # unit tests only (fast, run often)
make test-integration    # integration tests (needs DB running)
make tests               # all tests
make tests-coverage      # all + coverage report
```

From the repository root:

```bash
make tests-fast          # backend + frontend, uses .env.test and an already running test DB
make tests-compose       # starts isolated test PostgreSQL, runs tests, then stops containers
make test-env-up         # start isolated test PostgreSQL manually
make test-env-down       # stop isolated test PostgreSQL and remove its data
```

## Patterns

- Shared fixtures: `backend/tests/fixtures.py` — `FactoryFixture`, `StorageFixture`
- Unit-only fixtures: `backend/tests/unit/fixtures.py` — `ContainerFixture`, `ApiFixture` (re-exports `FactoryFixture`)
- Mock providers for unit tests: `backend/tests/unit/mocks/providers/`
- Test data factories in `backend/tests/helpers/factories/`: `CoreFactoryHelper` (domain objects), `ApiFactoryHelper` (request payloads) — plain Python, no Mimesis
- Access via `self.factory.core.*` / `self.factory.api.*` — inherit from `FactoryFixture`
- Unit test mocking: `Mock(spec=SomeStorageABC)` from `unittest.mock`
- API tests: inherit `ApiFixture` -> `self.api.*` / `self.no_auth_api.*`
- Integration DB tests: inherit `StorageFixture` -> `self.storage_helper.*`, session auto-rollbacks
- Add API helper methods in `backend/tests/helpers/api.py` instead of duplicating endpoint URL strings across tests.
- Create domain test objects through `self.factory.core.*`; direct dataclass construction is only for cases not covered by factories yet.
- Unit API tests verify HTTP contract and use case calls. Unit core tests verify branch logic. Storage behavior belongs in integration tests.
- Cover DB/storage changes with integration tests through `StorageFixture`.

## Coverage Target

95% — driven by unit tests and database integration tests.

Core layer should be 100% coverage.

## Test File Naming

`test_<action>_<expected_result>.py` — e.g. `test_create_item_returns_201.py`, `test_create_item_rejects_empty_title.py`
