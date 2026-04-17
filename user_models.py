from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    Enum as SAEnum, ARRAY, ForeignKey
)
from sqlalchemy import JSON  # JSON 임포트(테스트땜시..)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class AuthProvider(str, enum.Enum):
    LOCAL = "local"
    KAKAO = "kakao"
    GOOGLE = "google"

class FriendshipStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

# 사용자 모델 
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    unique_id = Column(String(6), unique=True, nullable=False, index=True) # 고유 ID(영어 숫자 혼합 6자리로)
    email = Column(String(255), unique=True, nullable=False, index=True)
    nickname = Column(String(50), nullable=False)
    hashed_password = Column(String(255), nullable=True)  # 소셜 로그인은 null
    #tags = Column(ARRAY(String), nullable=False, server_default="{}") 이게 postgresql
    tags = Column(JSON, default=[]) #테스트떔시
    auth_provider = Column(SAEnum(AuthProvider), nullable=False, default=AuthProvider.LOCAL)
    social_id = Column(String(255), nullable=True)  # 소셜 고유 ID
    is_active = Column(Boolean, default=True, nullable=False)
    is_email_verified = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 친구 관계 설정  
    sent_friend_requests = relationship(
        "Friendship",
        foreign_keys="Friendship.requester_id",
        back_populates="requester",
        lazy="selectin",
    )
    received_friend_requests = relationship(
        "Friendship",
        foreign_keys="Friendship.addressee_id",
        back_populates="addressee",
        lazy="selectin",
    )

#친구 모델
class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    # 요청 보낸 사람
    requester_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # 요청 받은 사람
    addressee_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    status = Column(SAEnum(FriendshipStatus), nullable=False, default=FriendshipStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # User 모델 연결
    requester = relationship("User", foreign_keys=[requester_id], back_populates="sent_friend_requests")
    addressee = relationship("User", foreign_keys=[addressee_id], back_populates="received_friend_requests")