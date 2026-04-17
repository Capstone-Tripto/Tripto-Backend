from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
import redis.asyncio as aioredis

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_ENV == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

class Base(DeclarativeBase): # DB 베이스 모델 
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Redis 관련 설정
_redis: aioredis.Redis = None

async def init_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True, # 가져온 데이터를 자동으로 문자열로 변환
        )

async def close_redis():
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None

async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        await init_redis()
    return _redis