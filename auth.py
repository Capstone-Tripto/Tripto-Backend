from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis
from fastapi.security import HTTPAuthorizationCredentials
import time

from app.core.database import get_db, get_redis
from app.api.dependencies import get_current_user, bearer_scheme
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from app.models.user_models import User  
from app.schemas.user_schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    EmailVerifyRequest,
    EmailVerifyConfirm,
    UserResponse,
    UserUpdateRequest,
)
from app.services.user_services import UserService 

router = APIRouter(prefix="/api/v1/auth")

# 서비스 인스턴스 생성
def get_user_service(db: AsyncSession = Depends(get_db), redis: aioredis.Redis = Depends(get_redis)):
    return UserService(db, redis)

# 이메일 인증 코드 발송
@router.post("/verification", summary="이메일 인증 코드 발송")
async def send_email_code(
    body: EmailVerifyRequest,
    service: UserService = Depends(get_user_service),
):
    await service.send_verification_email(body.email)
    return {"message": "인증 코드가 발송되었습니다. 5분 안에 입력해주세요."}

# 이메일 인증 코드 확인
@router.post("/verify-code", summary="이메일 인증 코드 확인")
async def check_email_code(
    body: EmailVerifyConfirm,
    redis: aioredis.Redis = Depends(get_redis),
):
    key = f"email_verify:{body.email}"
    stored = await redis.get(key)
    if not stored or (stored.decode('utf-8') if isinstance(stored, bytes) else stored) != body.code:
        raise HTTPException(status_code=400, detail="인증 코드가 올바르지 않거나 만료되었습니다.")
    return {"message": "인증 코드가 확인되었습니다."}

# 자체 회원가입 
@router.post("/register", response_model=UserResponse, status_code=201, summary="회원가입 완료")
async def register(
    body: RegisterRequest,
    service: UserService = Depends(get_user_service),
):
    user = await service.register_user(body)
    return user

# 자체 로그인 
@router.post("/login", response_model=TokenResponse, summary="로그인")
async def login(
    body: LoginRequest,
    service: UserService = Depends(get_user_service),
):
    tokens = await service.login_user(body.email, body.password)
    return TokenResponse(**tokens)