from collections.abc import Generator
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from dishka import AsyncContainer, make_async_container
from dishka.integrations.litestar import setup_dishka
from litestar import Litestar
from litestar.testing import TestClient
from sqlalchemy import NullPool, delete
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from config.initializers import create_base_app
from config.settings import settings, Settings
from db.models import CompetencyMatrixItemModel, ExternalResourceModel, UserModel
from db.utils import migrate, downgrade
from tests.mocks.auth.providers import MockAuthProvider
from tests.mocks.competency_matrix.providers import MockCompetencyMatrixProvider


@pytest.fixture(scope="session")
def test_settings() -> Generator[Settings, None, None]:
    settings.database.name = "my_site_database_test"
    yield settings
    settings.database.name = "my_site_database"


@pytest_asyncio.fixture(loop_scope="session")
async def container(test_settings: Settings) -> AsyncGenerator[AsyncContainer, None]:
    container = make_async_container(
        MockCompetencyMatrixProvider(),
        MockAuthProvider(settings=test_settings),
    )
    yield container
    await container.close()


@pytest.fixture
def app(container: AsyncContainer) -> Litestar:
    app = create_base_app(lifespan=[])
    setup_dishka(container=container, app=app)
    return app


@pytest.fixture
def client(app: Litestar) -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def engine(test_settings: Settings) -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(settings.database.url.get_secret_value(), poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def setup_migrations(engine: AsyncEngine, test_settings: Settings) -> Generator[None, None, None]:
    migrate(revision="heads")
    yield
    downgrade(revision="base")


@pytest_asyncio.fixture
async def clear_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.execute(delete(UserModel))
        await conn.execute(delete(ExternalResourceModel))
        await conn.execute(delete(CompetencyMatrixItemModel))


@pytest_asyncio.fixture
async def session(
    session_maker: async_sessionmaker[AsyncSession],
    setup_migrations: None,
    clear_tables: None,
) -> AsyncGenerator:
    async with session_maker() as db:
        yield db
        await db.commit()
