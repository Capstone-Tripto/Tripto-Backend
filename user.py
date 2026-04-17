from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user_models import User
from app.services.friendship_services import FriendService
from app.schemas.user_schemas import (
    UserResponse, UserUpdateRequest, FriendSearchResponse, 
    FriendListItem
)
#from app.models.plan_models import Plan # 일정 모델 만들어야댐

router = APIRouter(prefix="/api/v1/users/me")

def get_friend_service(db: AsyncSession = Depends(get_db)):
    return FriendService(db)

# 내 프로필 조회
@router.get("", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

# 프로필 생성
@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    body: UserUpdateRequest, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if body.nickname: current_user.nickname = body.nickname
    await db.commit()
    return current_user

# 여행 태그 선택
@router.post("/tags")
async def update_tags(tags: list[str], db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    current_user.tags = tags
    await db.commit()
    return {"message": "이제 트립토가 너의 여행 취향대로 끝내주는 코스를 짜주마.."}

# 친구 리스트 조회
@router.get("/friends", response_model=list[FriendListItem])
async def list_friends(current_user: User = Depends(get_current_user), service: FriendService = Depends(get_friend_service)):
    return await service.get_friend_list(current_user)

# 친구 검색
@router.get("/friends/search", response_model=FriendSearchResponse)
async def search_friend(unique_id: str, current_user: User = Depends(get_current_user), service: FriendService = Depends(get_friend_service)):
    return await service.search_user_by_unique_id(unique_id, current_user)

# 친구 추가
@router.post("/friends/search") 
async def add_friend(unique_id: str, current_user: User = Depends(get_current_user), service: FriendService = Depends(get_friend_service)):
    return await service.send_friend_request(unique_id, current_user)

# 친구 삭제
@router.delete("/friends")
async def delete_friend(friendship_id: int, current_user: User = Depends(get_current_user), service: FriendService = Depends(get_friend_service)):
    await service.remove_friend(friendship_id, current_user)
    return {"message": "삭제 완료"}

# 친구 여행 소식 리스트 조회
@router.get("/friends/travels", summary="친구 여행 소식 리스트 조회")
async def get_friend_travel_list(
    current_user: User = Depends(get_current_user),
    service: FriendService = Depends(get_friend_service)
):
    return await service.get_friend_travels(current_user)

"""
# 친구 여행 소식 상세 조회
@router.get("/friends/travels/{post_id}", summary="친구 여행 소식 상세 조회")
async def get_friend_travel_detail(
    post_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    result = await db.execute(select(Plan).where(Plan.id == post_id))
    plan = result.scalar_one_or_none()
    
    if not plan:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")
        
    # 작성자 정보 조회
    user_result = await db.execute(select(User).where(User.id == plan.user_id))
    author = user_result.scalar_one_or_none()
    
    return {
        "post_id": plan.id, 
        "friend_id": author.id, 
        "location": plan.location,
        "friend_nickname": author.nickname, 
        "title": plan.title, 
        "content": plan.content,
        "images": plan.images, 
        "places": [], # 상세 장소 로직 추가 필요함
        "participants": plan.participants,
        "start_date": plan.start_date, 
        "end_date": plan.end_date
    }
"""

"""
# 알림 설정
@router.patch("/notifications", summary="알림 설정 변경")
async def update_notifications(
    payload: NotificationUpdate, # user_schemas.py에 정의 필요
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    current_user.is_notify = payload.enabled
    await db.commit()
    return {"message": "알림 설정이 업데이트되었습니다."}
"""