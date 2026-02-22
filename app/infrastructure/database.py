import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Read database URL from environment; default points to local postgres
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/fce",
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()


async def init_db() -> None:
    """Create database tables defined on `Base`.

    Intended to be called from a startup script or `scripts/seed_data.py`.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
