from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config.settings import settings

engine = create_async_engine(
    settings.database.url.get_secret_value(),
    pool_pre_ping=settings.database.pool_pre_ping,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
)

sessionmaker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=settings.database.expire_on_commit,
)
