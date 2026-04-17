from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from fastapi import HTTPException, status
from app.models.user_models import User, Friendship, FriendshipStatus
from app.schemas.user_schemas import FriendListItem, FriendSearchResponse, FriendRequestResponse
#from app.models.plan_models import Plan 

class FriendService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ID로 사용자 검색 
    async def search_user_by_unique_id(
        self,
        unique_id: str,
        current_user: User,
    ) -> FriendSearchResponse:
        if unique_id == current_user.unique_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="자기 자신의 ID는 검색할 수 없습니다.",
            )

        result = await self.db.execute(select(User).where(User.unique_id == unique_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 ID의 사용자를 찾을 수 없습니다.",
            )

        return FriendSearchResponse.model_validate(user)

    # 친구 요청 보내기
    async def send_friend_request(
        self,
        target_unique_id: str,
        current_user: User,
    ) -> FriendRequestResponse:
        # 대상 유저 조회
        result = await self.db.execute(select(User).where(User.unique_id == target_unique_id))
        target = result.scalar_one_or_none()

        if not target:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        if target.id == current_user.id:
            raise HTTPException(status_code=400, detail="자기 자신에게 친구 요청을 보낼 수 없습니다.")

        # 기존 관계 확인
        existing = await self.db.execute(
            select(Friendship).where(
                or_(
                    and_(
                        Friendship.requester_id == current_user.id,
                        Friendship.addressee_id == target.id,
                    ),
                    and_(
                        Friendship.requester_id == target.id,
                        Friendship.addressee_id == current_user.id,
                    ),
                )
            )
        )
        rel = existing.scalar_one_or_none()

        if rel:
            if rel.status == FriendshipStatus.ACCEPTED:
                raise HTTPException(status_code=409, detail="이미 친구입니다.")
            if rel.status == FriendshipStatus.PENDING:
                raise HTTPException(status_code=409, detail="이미 친구 요청이 전송되었습니다.")
            if rel.status == FriendshipStatus.BLOCKED:
                raise HTTPException(status_code=403, detail="차단된 사용자입니다.")

        friendship = Friendship(
            requester_id=current_user.id,
            addressee_id=target.id,
            status=FriendshipStatus.PENDING,
        )
        self.db.add(friendship)
        await self.db.flush()
        await self.db.refresh(friendship)
        return FriendRequestResponse.model_validate(friendship)

    # 받은 친구 요청 목록
    async def get_received_requests(
        self,
        current_user: User,
    ) -> list[FriendRequestResponse]:
        result = await self.db.execute(
            select(Friendship).where(
                Friendship.addressee_id == current_user.id,
                Friendship.status == FriendshipStatus.PENDING,
            )
        )
        friendships = result.scalars().all()
        return [FriendRequestResponse.model_validate(f) for f in friendships]

    # 친구 요청 수락/거절 
    async def respond_to_friend_request(
        self,
        friendship_id: int,
        action: str,  # "accept" or "reject"
        current_user: User,
    ) -> FriendRequestResponse:
        result = await self.db.execute(
            select(Friendship).where(
                Friendship.id == friendship_id,
                Friendship.addressee_id == current_user.id,
                Friendship.status == FriendshipStatus.PENDING,
            )
        )
        friendship = result.scalar_one_or_none()

        if not friendship:
            raise HTTPException(status_code=404, detail="친구 요청을 찾을 수 없습니다.")

        if action == "accept":
            friendship.status = FriendshipStatus.ACCEPTED
        elif action == "reject":
            friendship.status = FriendshipStatus.REJECTED
        else:
            raise HTTPException(status_code=400, detail="action은 'accept' 또는 'reject'여야 합니다.")

        await self.db.flush()
        await self.db.refresh(friendship)
        return FriendRequestResponse.model_validate(friendship)

    # 친구 목록 보기
    async def get_friend_list(
        self,
        current_user: User,
    ) -> list[FriendListItem]:
        result = await self.db.execute(
            select(Friendship).where(
                or_(
                    Friendship.requester_id == current_user.id,
                    Friendship.addressee_id == current_user.id,
                ),
                Friendship.status == FriendshipStatus.ACCEPTED,
            )
        )
        friendships = result.scalars().all()

        items = []
        for f in friendships:
            friend_user = f.addressee if f.requester_id == current_user.id else f.requester
            items.append(
                FriendListItem(
                    friendship_id=f.id,
                    user=FriendSearchResponse.model_validate(friend_user),
                    since=f.updated_at or f.created_at,
                )
            )
        return items

    """
    # 친구 여행 소식 리스트 조회 
    async def get_friend_travels(
        self,
        current_user: User,
    ) -> list:
        friend_list = await self.get_friend_list(current_user)
        friend_ids = [f.user.id for f in friend_list]
        
        if not friend_ids:
            return []
        
        result = await self.db.execute(
            select(Plan)
            .where(Plan.user_id.in_(friend_ids))
            .order_by(Plan.created_at.desc()) # 최신순 정렬
        )
        plans = result.scalars().all()
        
        return plans
        """

    # 친구 삭제
    async def remove_friend(
        self,
        friendship_id: int,
        current_user: User,
    ) -> None:
        result = await self.db.execute(
            select(Friendship).where(
                Friendship.id == friendship_id,
                or_(
                    Friendship.requester_id == current_user.id,
                    Friendship.addressee_id == current_user.id,
                ),
                Friendship.status == FriendshipStatus.ACCEPTED,
            )
        )
        friendship = result.scalar_one_or_none()

        if not friendship:
            raise HTTPException(status_code=404, detail="친구 관계를 찾을 수 없습니다.")

        await self.db.delete(friendship)
        await self.db.commit()