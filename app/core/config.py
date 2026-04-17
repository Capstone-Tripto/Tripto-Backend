from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "트립토"
    APP_ENV: str = "development"

    SECRET_KEY: str # 보안 키
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 데이터
    DATABASE_URL: str 
    REDIS_URL: str 

    # 이메일 인증 
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""
    EMAIL_CODE_TTL: int = 300 # 인증번호 유효시간 300초

    # 카카오 로그인
    KAKAO_CLIENT_ID: str = ""
    KAKAO_REDIRECT_URI: str = ""

    # 구글 로그인
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""

    # 프론트 통신 주소 
    FRONTEND_URL: str = ""    

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()

# 다른 모듈에서 from config import settings로 바로 이용 가능 
settings = get_settings()