import random
import string
import httpx
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.user_models import User
from app.schemas.user_schemas import RegisterRequest
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.core.config import settings

class UserService:
    def __init__(self, db: AsyncSession, redis: aioredis.Redis):
        self.db = db
        self.redis = redis

    # 고유 ID(unique_id) 생성 
    def _generate_candidate_id(self) -> str: # 숫자 + 알파벳(대소문자) 6자 고유 ID 생성
        chars = string.ascii_letters + string.digits
        # 최소 1개 숫자, 1개 알파벳 보장
        must_have = [
            random.choice(string.digits),
            random.choice(string.ascii_letters),
        ]
        rest = [random.choice(chars) for _ in range(4)]
        combined = must_have + rest
        random.shuffle(combined)
        return "".join(combined)

    async def _get_unique_id(self) -> str: # 중복 없는 고유 ID 반환 최대 10회 반복
        for _ in range(10):
            candidate = self._generate_candidate_id()
            result = await self.db.execute(select(User).where(User.unique_id == candidate))
            if result.scalar_one_or_none() is None:
                return candidate
        raise HTTPException(status_code=500, detail="고유 ID 생성에 실패했습니다. 잠시 후 다시 시도해주세요.")

    # 이메일 인증 관련 함수
    def _generate_verification_code(self, length: int = 6) -> str: # 이메일 인증 번호 생성 
        return "".join(random.choices(string.digits, k=length))

    async def send_verification_email(self, email: str) -> None: # 인증 코드 Redis 저장 및 이메일 발송
        code = self._generate_verification_code()
        key = f"email_verify:{email}"
        await self.redis.setex(key, settings.EMAIL_CODE_TTL, code)
        # 메일 메시지 형식
        message = MIMEMultipart("alternative")
        message["Subject"] = f"[트립토] 사용자 이메일 인증 코드: {code}"
        message["From"] = settings.EMAIL_FROM
        message["To"] = email

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background: #f4f6fb; padding: 40px;">
          <div style="max-width: 480px; margin: auto; background: white; border-radius: 12px; padding: 40px; box-shadow: 0 2px 12px rgba(0,0,0,0.08);">
            <h2 style="color: #3B82F6; margin-bottom: 8px;">✈️ 트립토</h2>
            <h3 style="color: #1e293b;">이메일 인증 코드</h3>
            <p style="color: #475569;">아래 인증 코드를 입력해주세요. 코드는 5분간 유효합니다.</p>
            <div style="background: #EFF6FF; border-radius: 8px; padding: 24px; text-align: center; margin: 24px 0;">
              <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #2563EB;">{code}</span>
            </div>
          </div>
        </body>
        </html>
        """
        message.attach(MIMEText(html_body, "html"))

        # 비동기 메일 발송
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )

    async def _verify_email_code(self, email: str, code: str) -> bool: # Redis에서 인증 코드 검증 후 삭제
        key = f"email_verify:{email}"
        stored_code = await self.redis.get(key)
        if stored_code == code:
            await self.redis.delete(key)
            return True
        return False

    # 앱 자체 회원가입/로그인 
    async def register_user(self, user_data: RegisterRequest):
        # 인증번호 확인
        if not await self._verify_email_code(user_data.email, user_data.verification_code):
            raise HTTPException(status_code=400, detail="인증 코드가 틀렸거나 만료됐잖슴~! 다시 시도해야하잖슴~!")

        # 중복 확인
        if await self._get_user_by_email(user_data.email):
            raise HTTPException(status_code=400, detail="이미 가입했던 이메일이잖슴...")

        # 고유 6자리 ID 생성 호출
        unique_id = await self._get_unique_id()

        new_user = User(
            unique_id=unique_id,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            nickname=user_data.nickname,
            tags=user_data.tags,
            auth_provider="local",
            is_active=True
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return self._generate_auth_tokens(new_user)

    async def login_user(self, email: str, password: str):
        user = await self._get_user_by_email(email)
        if not user or not user.hashed_password or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 잘못되었습니다.")
        return self._generate_auth_tokens(user)
    
    # (이하 _get_user_by_email, _generate_auth_tokens 등 공통 부분 원본 유지)

    # 카카오/구글 소셜 로그인
    async def kakao_login(self, code: str):
        async with httpx.AsyncClient() as client:
            # 토큰 요청
            resp = await client.post("https://kauth.kakao.com/oauth/token", data={
                "grant_type": "authorization_code",
                "client_id": settings.KAKAO_CLIENT_ID,
                "redirect_uri": settings.KAKAO_REDIRECT_URI,
                "code": code,
            })
            token_data = resp.json()
            # 사용자 정보 요청
            user_resp = await client.get("https://kapi.kakao.com/v2/user/me", 
                                        headers={"Authorization": f"Bearer {token_data.get('access_token')}"})
            user_info = user_resp.json()
            email = user_info.get("kakao_account", {}).get("email")
            nickname = user_info.get("kakao_account", {}).get("profile", {}).get("nickname", "카카오유저")

        return await self._social_login_logic(email, nickname, "kakao")

    async def google_login(self, code: str):
        async with httpx.AsyncClient() as client:
            # 토큰 요청
            resp = await client.post("https://oauth2.googleapis.com/token", data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            })
            token_data = resp.json()
            # 사용자 정보 요청
            user_resp = await client.get("https://www.googleapis.com/oauth2/v2/userinfo",
                                        headers={"Authorization": f"Bearer {token_data.get('access_token')}"})
            user_info = user_resp.json()
            email = user_info.get("email")
            nickname = user_info.get("name", "구글유저")

        return await self._social_login_logic(email, nickname, "google")

    # 공통 부분 
    async def _social_login_logic(self, email: str, nickname: str, provider: str):
        user = await self._get_user_by_email(email)
        if not user:
            unique_id = await self._get_unique_id()
            user = User(
                unique_id=unique_id,
                email=email, 
                nickname=nickname, 
                auth_provider=provider, 
                is_active=True
            )
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
        return self._generate_auth_tokens(user)

    async def _get_user_by_email(self, email: str):
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    def _generate_auth_tokens(self, user: User):
        return {
            "access_token": create_access_token(data={"sub": str(user.id)}),
            "refresh_token": create_refresh_token(data={"sub": str(user.id)}),
            "token_type": "bearer"
        }