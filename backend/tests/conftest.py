import uuid
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from infra.config.settings import Settings, settings


@pytest.fixture
def global_random_uuid() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def global_random_hex_uuid(global_random_uuid: uuid.UUID) -> str:
    return global_random_uuid.hex


@pytest.fixture(scope="session")
def test_settings() -> Generator[Settings]:
    original_use_cache = settings.app.use_cache
    original_database_name = settings.database.name
    settings.database.name = "my_site_database_test"
    settings.app.use_cache = False
    yield settings
    settings.app.use_cache = original_use_cache
    settings.database.name = original_database_name


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def engine(test_settings: Settings) -> AsyncGenerator[AsyncEngine]:
    _ = test_settings
    engine = create_async_engine(settings.database.url.get_secret_value(), poolclass=NullPool)
    yield engine
    await engine.dispose()
