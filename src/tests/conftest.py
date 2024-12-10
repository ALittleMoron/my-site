from collections.abc import AsyncGenerator, Generator, Mapping

import pytest
import pytest_asyncio
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import TestClient
from sqlalchemy import NullPool, delete
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.deps import dependencies
from app.config import settings
from app.database.models import (
    CompetencyMatrixItemModel,
    GradeModel,
    ResourceModel,
    SectionModel,
    SheetModel,
    SubsectionModel,
)
from app.database.models.competency_matrix import items_to_resources
from app.database.storages import DatabaseStorage
from app.main import create_app, get_plugins
from tests.mocks.storage_mock import MockCompetencyMatrixStorage
from tests.mocks.use_cases.list_competency_matrix_items import MockListCompetencyMatrixItems
from tests.utils import provide_async


@pytest.fixture(scope="session")
def mock_storage() -> MockCompetencyMatrixStorage:
    return MockCompetencyMatrixStorage()


@pytest.fixture(scope="session")
def mock_list_competency_matrix_items_use_case() -> MockListCompetencyMatrixItems:
    return MockListCompetencyMatrixItems()


@pytest.fixture(scope="session")
def app_dependencies(
    mock_storage: MockCompetencyMatrixStorage,
    mock_list_competency_matrix_items_use_case: MockListCompetencyMatrixItems,
) -> Mapping[str, Provide]:
    deps = {
        'storage': provide_async(mock_storage),
        'list_competency_matrix_items_use_case': provide_async(
            mock_list_competency_matrix_items_use_case,
        ),
    }
    deps.update({key: value for key, value in dependencies.items() if key not in deps})
    return deps


@pytest.fixture(scope="session")
def app() -> Litestar:
    return create_app(  # type: ignore[no-any-return]
        debug=True,
        plugins=get_plugins(),
        deps=dependencies,
    )


@pytest.fixture(scope="session")
def client(app: Litestar) -> "Generator[TestClient, None, None]":
    with TestClient(app=app) as client:
        yield client


@pytest.fixture(scope="session")
def mocked_app(app_dependencies: Mapping[str, Provide]) -> Litestar:
    return create_app(  # type: ignore[no-any-return]
        debug=True,
        plugins=get_plugins(),
        deps=app_dependencies,
    )


@pytest.fixture(scope="session")
def mocked_client(mocked_app: Litestar) -> "Generator[TestClient[Litestar], None, None]":
    with TestClient(app=mocked_app) as client:
        yield client


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(settings.database.url.get_secret_value(), poolclass=NullPool)
    yield engine
    await engine.dispose()


@pytest.fixture(scope="session")
async def sessionmaker(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def clear_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.execute(delete(CompetencyMatrixItemModel))
        await conn.execute(delete(items_to_resources))
        await conn.execute(delete(ResourceModel))
        await conn.execute(delete(SubsectionModel))
        await conn.execute(delete(SectionModel))
        await conn.execute(delete(GradeModel))
        await conn.execute(delete(SheetModel))


@pytest.fixture
async def session(
    sessionmaker: async_sessionmaker,
    engine: AsyncEngine,
    clear_tables: None,
) -> AsyncGenerator[AsyncSession, None]:
    async with sessionmaker(bind=engine) as db:
        yield db
        await db.commit()


@pytest.fixture
def storage(session: AsyncSession) -> DatabaseStorage:
    return DatabaseStorage(session=session)
