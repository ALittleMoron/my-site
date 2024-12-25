from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from litestar import Litestar
from litestar.testing import TestClient
from sqlalchemy import NullPool, delete
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from verbose_http_exceptions.ext.litestar import ALL_EXCEPTION_HANDLERS_MAP

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


@pytest.fixture(scope="session")
def app() -> Litestar:
    return create_app(  # type: ignore[no-any-return]
        debug=True,
        plugins=get_plugins(),
        deps=dependencies,
        exception_handlers=ALL_EXCEPTION_HANDLERS_MAP,
    )


@pytest.fixture(scope="session")
def client(app: Litestar) -> "Generator[TestClient, None, None]":
    with TestClient(app=app) as client:
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
