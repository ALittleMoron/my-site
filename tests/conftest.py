import uuid
from collections.abc import Generator
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from dishka import AsyncContainer, make_async_container
from dishka.integrations.litestar import LitestarProvider, setup_dishka
from litestar import Litestar
from litestar.testing import TestClient
from sqlalchemy import NullPool, delete
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

from config.settings import settings, Settings
from core.auth.enums import RoleEnum
from core.auth.schemas import JwtUser
from db.models import CompetencyMatrixItemModel, ExternalResourceModel, UserModel
from db.utils import migrate, downgrade
from entrypoints.litestar.initializers import create_litestar_app
from tests.mocks.providers.auth import MockAuthProvider
from tests.mocks.providers.competency_matrix import MockCompetencyMatrixProvider
from tests.mocks.providers.contacts import MockContactsProvider
from tests.mocks.providers.files import MockFilesProvider
from tests.mocks.providers.general import MockGeneralProvider


@pytest.fixture(scope="session")
def global_random_uuid() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture(scope="session")
def test_settings() -> Generator[Settings, None, None]:
    settings.database.name = "my_site_database_test"
    yield settings
    settings.database.name = "my_site_database"


@pytest.fixture
def random_suffix(global_random_uuid: uuid.UUID) -> str:
    return global_random_uuid.hex[:8]


@pytest_asyncio.fixture(loop_scope="function")
async def container(
    test_settings: Settings,
    global_random_uuid: uuid.UUID,
    random_suffix: str,
) -> AsyncGenerator[AsyncContainer, None]:
    container = make_async_container(
        LitestarProvider(),
        MockGeneralProvider(uuid_=global_random_uuid),
        MockFilesProvider(random_suffix=random_suffix),
        MockCompetencyMatrixProvider(),
        MockContactsProvider(),
        MockAuthProvider(settings=test_settings),
    )
    yield container
    await container.close()


@pytest.fixture
def app(container: AsyncContainer) -> Litestar:
    app = create_litestar_app(lifespan=[], container=container)
    setup_dishka(container=container, app=app)
    return app


@pytest.fixture
def jwt_user() -> JwtUser:
    return JwtUser(username="test", role=RoleEnum.USER)


@pytest.fixture
def jwt_admin() -> JwtUser:
    return JwtUser(username="test", role=RoleEnum.ADMIN)


@pytest.fixture
def no_auth_client(app: Litestar) -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def client(app: Litestar) -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        client.headers["Authorization"] = f"Bearer ANY"
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
