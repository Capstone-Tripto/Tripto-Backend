from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.user import router as friendship_router
from app.core.database import engine, Base, init_redis, close_redis
from app.models.user_models import User, Friendship  # noqa: F401

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작
    await init_redis()
    # 개발 환경에서 테이블 자동 생성되게 (운영은 Alembic 사용)
    if settings.APP_ENV == "development":
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    # 종료
    await close_redis()
    await engine.dispose()


app = FastAPI(
    title="트립토 API",
    description="트립토 백엔드 API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth_router)
app.include_router(friendship_router)


@app.get("/health") # 서버 살아있는지 확인하는 용도 
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}