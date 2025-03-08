from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Sync engine for migrations and utilities
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async engine for main application
ASYNC_SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
async_engine = create_async_engine(ASYNC_SQLALCHEMY_DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass


# Dependency to get DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()