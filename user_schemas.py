from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from app.models.user_models import AuthProvider, FriendshipStatus

# 회원가입
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nickname: str
    tags: List[str] = []
    verification_code: str  # 이메일 인증 코드

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")
        return v

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 20:
            raise ValueError("닉네임은 2~20자 사이여야 합니다.")
        return v

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        if len(v) > 10:
            raise ValueError("태그는 최대 10개까지 가능합니다.")
        return [t.strip() for t in v if t.strip()]

# 이메일 인증 코드 요청 
class EmailVerifyRequest(BaseModel):
    email: EmailStr

class EmailVerifyConfirm(BaseModel):
    email: EmailStr
    code: str

# 로그인
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# 토큰 
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# 소셜 로그인
class OAuthCallbackRequest(BaseModel):
    code: str
    state: Optional[str] = None


#  사용자한테 응답으로 돌려줘도 되는거
class UserResponse(BaseModel):
    id: int
    unique_id: str
    email: str
    nickname: str
    tags: List[str]
    auth_provider: AuthProvider
    is_email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class UserUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    tags: Optional[List[str]] = None

# 친구 검색 결과
class FriendSearchResponse(BaseModel):
    id: int
    unique_id: str
    nickname: str
    tags: List[str]

    model_config = {"from_attributes": True}

# 친구 요청 생성
class FriendRequestCreate(BaseModel):
    unique_id: str  # 상대방 고유 ID

# 친구 요청 응답 
class FriendRequestResponse(BaseModel):
    id: int
    requester_id: int
    addressee_id: int
    status: FriendshipStatus
    created_at: datetime
    requester: FriendSearchResponse
    addressee: FriendSearchResponse

    model_config = {"from_attributes": True}

# 친구 요청 수락/거절
class FriendRequestAction(BaseModel):
    friendship_id: int
    action: str  # "accept" or "reject"

# 친구 목록 아이템
class FriendListItem(BaseModel):
    friendship_id: int
    user: FriendSearchResponse
    since: datetime

    model_config = {"from_attributes": True}