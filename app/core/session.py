from typing import AsyncGenerator

from sqlalchemy import create_engine as create_sync_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


engine = create_async_engine(
    settings.async_database_url,
    echo=settings.debug,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


sync_engine = create_sync_engine(
    settings.sync_database_url,
    echo=settings.debug,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def get_sync_db():
    from sqlalchemy.orm import Session as SyncSession

    SyncSessionLocal = sessionmaker(
        sync_engine,
        class_=SyncSession,
        expire_on_commit=False,
    )
    db = SyncSessionLocal()
    try:
        yield db
    finally:
        db.close()
