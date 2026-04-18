---
paths:
  - "backend_tests/**/*.py"
---

# Backend testing rules

## Philosophy

TDD. Tests drive implementation. Unit tests cover all logic branches. Integration tests cover success paths only.

## Unit vs. integration tests

| Type | Definition | Directory |
|---|---|---|
| **Unit** | Single layer in isolation. Uses mock storages/providers. | `backend_tests/unit/` |
| **Integration** | DB storages + core together, no mocks. Happy path only. | `backend_tests/integration/` |

### Unit tests

- Test a single layer in isolation. Any directory can have unit tests.
- No real DB, no real external services
- Mock storages via `Mock(spec=SomeStorageABC)`
- Test every branch: happy path, validation errors, domain exceptions
- Inherit `FactoryFixture` for `self.factory.core.*` / `self.factory.api.*`

### Integration tests

- Test the full stack: HTTP → handler → use case → real DB (no mocks anywhere).
- Happy path only
- Real PostgreSQL test DB (`my_site_database_test`) — auto-migrated via conftest
- Real Dishka providers (not mocks)
- Inherit `StorageFixture` for DB assertion helpers; session auto-rollbacks after each test

### Commands

```bash
make test-unit           # unit tests only (fast, run often)
make test-integration    # integration tests (needs DB running)
make tests               # all tests
make tests-coverage      # all + coverage report
```

## Patterns

- Shared fixtures: `backend_tests/fixtures.py` — `FactoryFixture`, `StorageFixture`
- Unit-only fixtures: `backend_tests/unit/fixtures.py` — `ContainerFixture`, `ApiFixture` (re-exports `FactoryFixture`)
- Mock providers for unit tests: `backend_tests/unit/mocks/providers/`
- Test data factories in `backend_tests/helpers/factories/`: `CoreFactoryHelper` (domain objects), `ApiFactoryHelper` (request payloads) — plain Python, no Mimesis
- Access via `self.factory.core.*` / `self.factory.api.*` — inherit from `FactoryFixture`
- Unit test mocking: `Mock(spec=SomeStorageABC)` from `unittest.mock`
- API tests: inherit `ApiFixture` → `self.api.*` / `self.no_auth_api.*`
- Integration DB tests: inherit `StorageFixture` → `self.storage_helper.*`, session auto-rollbacks

## Coverage target

**95%** — driven by unit tests and database integration tests.

Core layer should be 100% coverage.

## Test file naming

`test_<action>_<expected_result>.py` — e.g. `test_create_item_returns_201.py`, `test_create_item_rejects_empty_title.py`
