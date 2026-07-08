from collections.abc import Generator

import pytest

from infra.postgresql.utils import downgrade, migrate
from tests.helpers.assertions import AssertsHelper


@pytest.fixture
def migrated_to_0001() -> Generator[None]:
    migrate(revision="0001")
    yield
    downgrade(revision="base")


@pytest.fixture
def migrated_to_0002() -> Generator[None]:
    migrate(revision="0002")
    yield
    downgrade(revision="base")


@pytest.fixture
def migrated_to_0004() -> Generator[None]:
    migrate(revision="0004")
    yield
    downgrade(revision="base")


@pytest.fixture
def migrated_to_0005() -> Generator[None]:
    migrate(revision="0005")
    yield
    downgrade(revision="base")


@pytest.fixture
def migration_asserts() -> AssertsHelper:
    return AssertsHelper()
