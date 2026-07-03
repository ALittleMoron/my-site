from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from infra.config.settings import Settings
from infra.postgresql.models import (
    ArticleDailyAnalyticsModel,
    ArticleFileUsageModel,
    ArticleModel,
    ArticleReactionModel,
    ArticleToTagSecondaryModel,
    CompetencyMatrixItemModel,
    ExternalResourceModel,
    FileModel,
    TagModel,
    UserModel,
)
from infra.postgresql.utils import downgrade, migrate


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def session_maker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="package")
def setup_migrations(engine: AsyncEngine, test_settings: Settings) -> Generator[None]:
    _ = engine, test_settings
    migrate(revision="heads")
    yield
    downgrade(revision="base")


@pytest_asyncio.fixture
async def clear_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.execute(delete(UserModel))
        await conn.execute(delete(ExternalResourceModel))
        await conn.execute(delete(CompetencyMatrixItemModel))
        await conn.execute(delete(ArticleFileUsageModel))
        await conn.execute(delete(ArticleReactionModel))
        await conn.execute(delete(ArticleDailyAnalyticsModel))
        await conn.execute(delete(ArticleToTagSecondaryModel))
        await conn.execute(delete(ArticleModel))
        await conn.execute(delete(FileModel))
        await conn.execute(delete(TagModel))


@pytest_asyncio.fixture
async def session(
    session_maker: async_sessionmaker[AsyncSession],
    setup_migrations: None,
    clear_tables: None,
) -> AsyncGenerator:
    _ = setup_migrations, clear_tables
    async with session_maker() as db:
        yield db
        await db.commit()
