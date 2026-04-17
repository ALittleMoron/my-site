# Testing

## Philosophy

TDD. Write the test first. Run it, watch it fail, then implement.
Unit tests cover all logic branches. Integration tests cover success paths only.

## Test split

The split is defined by **whether mocks are used**, not by directory.

| Type | Definition | Marker | Speed | DB needed |
|---|---|---|---|---|
| **Unit** | Tests a single layer in isolation. Uses mock storages / providers. | *(none)* | Fast | No |
| **Integration** | Tests API + core + DB together, no mocks. | `@pytest.mark.integration` | Slower | Yes |

Any test without `@pytest.mark.integration` is a unit test.

## Commands

```bash
make test-unit           # all tests without @pytest.mark.integration (run constantly during TDD)
make test-integration    # only @pytest.mark.integration tests (run before commit, needs DB)
make tests               # all tests
make tests-coverage      # all + coverage report
```

## Coverage target

**95%** — driven by unit tests.
Raise `--fail-under` in `pyproject.toml` incrementally as unit coverage grows.

## Unit tests

Test a single layer in isolation. Any directory can have unit tests.

```python
class TestListItemsUseCase(FactoryFixture):
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.storage = Mock(spec=CompetencyMatrixStorage)
        self.use_case = ListItemsUseCase(storage=self.storage)

    async def test_returns_only_published(self) -> None:
        self.storage.list_items.return_value = [
            self.factory.core.competency_matrix_item(publish_status=PublishStatusEnum.DRAFT),
        ]
        result = await self.use_case.execute(only_published=True)
        assert result.values == []
```

Rules:
- No real DB, no real external services
- Mock storages via `Mock(spec=SomeStorageABC)`
- Test every branch: happy path, validation errors, domain exceptions
- Inherit `FactoryFixture` for `self.factory.core.*` / `self.factory.api.*`

## Integration tests

Test the full stack: HTTP → handler → use case → real DB (no mocks anywhere).
Mark with `@pytest.mark.integration`.

```python
@pytest.mark.integration
class TestCreateBlogPostIntegration(ApiFixture, StorageFixture):
    async def test_creates_post(self) -> None:
        response = self.api.post("/api/blog/posts", json=self.factory.api.create_blog_post())
        assert response.status_code == 201
```

Rules:
- Happy path only — one `@pytest.mark.integration` test per endpoint
- Real PostgreSQL test DB (`my_site_database_test`) — auto-migrated via conftest
- Real Dishka providers (not mocks)
- Inherit `StorageFixture` for DB assertion helpers; session auto-rollbacks after each test

## Fixtures

### Base fixture classes (`tests/fixtures.py`)

| Class | Provides | Use when |
|---|---|---|
| `FactoryFixture` | `self.factory.core.*`, `self.factory.api.*` | Any test that needs domain objects or request payloads |
| `ApiFixture` | `self.api.*`, `self.no_auth_api.*` | API endpoint tests (unit or integration) |
| `StorageFixture` | `self.storage_helper.*`, session auto-rollback | Integration tests that assert DB state |
| `ContainerFixture` | `self.container.*` | Tests that need DI container access |

### Pytest fixtures (`tests/conftest.py`)

| Fixture | Scope | Description |
|---|---|---|
| `test_settings` | session | Settings pointing to test DB |
| `jwt_user` | function | Authenticated `JwtUser` (USER role) |
| `global_random_uuid` | function | Random UUID for test isolation |
| `global_random_int` | function | Random int for test isolation |

### Test data factories (`tests/helpers/factories/`)

Plain Python. No Mimesis.
- `CoreFactoryHelper` — builds domain schemas (`CompetencyMatrixItem`, `BlogPost`, etc.)
- `ApiFactoryHelper` — builds API request payloads (dicts)

### Mock providers (`tests/mocks/providers/`)

One mock provider per domain. Replaces real Dishka providers in unit tests.
Uses in-memory storage — no DB access.

## Test file naming

`test_<action>_<expected_result>.py` — e.g. `test_create_item_returns_201.py`, `test_create_item_rejects_empty_title.py`

## Running integration tests locally

Services must be running:
```bash
make run                 # start docker compose (PG, Valkey, MinIO)
make test-integration    # in another terminal
```

## Pre-commit hooks

Configured via `.pre-commit-config.yaml`:
- ruff (lint + format)
- mypy (type check)
- pytest (unit tests only — `make test-unit`)

Run manually: `uv run pre-commit run --all-files`
