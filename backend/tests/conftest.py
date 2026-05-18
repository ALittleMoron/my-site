import secrets
import uuid
from collections.abc import Generator

import pytest

from core.types import IntId
from infra.config.settings import Settings, settings


@pytest.fixture
def global_random_uuid() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def global_random_int() -> IntId:
    return IntId(secrets.randbelow(20_000_001) - 10_000_000)


@pytest.fixture(scope="session")
def test_settings() -> Generator[Settings]:
    settings.database.name = "my_site_database_test"
    yield settings
    settings.database.name = "my_site_database"
