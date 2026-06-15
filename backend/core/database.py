import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from core.config import settings
from typing import Optional

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


# Use SQLite if PostgreSQL is not configured (free, no server needed)
_db_url = settings.DATABASE_URL
_use_sqlite = "sqlite" in _db_url

if _use_sqlite:
    logger.info("Using SQLite (free, no database server required)")
    # SQLite doesn't need asyncpg
    _db_url = settings.DATABASE_URL

engine = create_async_engine(
    _db_url,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if _use_sqlite else {},
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

redis_client = None  # Redis is optional now


async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_redis():
    if settings.REDIS_URL:
        try:
            from redis.asyncio import Redis
            global redis_client
            redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
            logger.info("Redis connected")
        except Exception as e:
            logger.warning(f"Redis not available (non-critical): {e}")
            redis_client = None
    else:
        logger.info("Redis not configured - using in-memory fallback")


async def close_redis():
    global redis_client
    if redis_client:
        try:
            await redis_client.close()
        except:
            pass


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def close_db():
    await engine.dispose()
