import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from core.database import Base, async_session_factory
from core.config import settings


@pytest.fixture(scope="session")
def event_loop():
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_db():
    """Create tables before each test using SQLite (free, no server needed)."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest.fixture
def sample_load_data():
    return {
        "origin_city": "Dubai",
        "destination_city": "Abu Dhabi",
        "pickup_date": "2025-01-15T08:00:00Z",
        "weight_kg": 5000,
        "commodity": "Electronics",
        "load_type": "ftl",
    }


@pytest.fixture
def sample_user_data():
    return {
        "email": "test@freightgpt.ae",
        "password": "testpassword123",
        "full_name": "Test User",
        "role": "tenant_admin",
    }
