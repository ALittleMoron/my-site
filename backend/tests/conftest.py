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
    original_use_cache = settings.app.use_cache
    original_database_name = settings.database.name
    settings.database.name = "my_site_database_test"
    settings.app.use_cache = False
    yield settings
    settings.app.use_cache = original_use_cache
    settings.database.name = original_database_name
