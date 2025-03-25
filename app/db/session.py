# app/db/session.py

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# Async engine
engine = create_async_engine(settings.DATABASE_URL, echo=False)

# Async session factory
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Dependency injectable session
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


# Declarative base class with async support
class Base(AsyncAttrs, DeclarativeBase):
    pass
