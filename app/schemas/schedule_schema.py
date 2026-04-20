import datetime
from typing import List, Optional, TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field

from app.models.schedule_model import ScheduleCategoryEnum
from app.schemas.memo_schema import MemoResponse

if TYPE_CHECKING:
    from app.schemas.memo_schema import MemoResponse


class Schedule(BaseModel):
    day_number: int = Field(..., ge=1, description="몇 일차 (1-based)")
    date: datetime.date = Field(..., description="해당 일정 날짜")
    order_index: int = Field(0, ge=0, description="같은 날 내 방문 순서")
    place_name: str = Field(..., examples=["성산일출봉"])
    place_address: Optional[str] = Field(None, examples=["제주 서귀포시 성산읍 일출로 284-12"])
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="위도")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="경도")
    category: ScheduleCategoryEnum = Field(ScheduleCategoryEnum.ETC, description="장소 카테고리")
    cost: Optional[int] = Field(None, ge=0, description="예상 비용 (원, 0=무료, None=미입력)")
    start_time: Optional[datetime.time] = Field(None, description="방문 시작 시각 (타임라인 뷰)")
    end_time: Optional[datetime.time] = Field(None, description="방문 종료 시각 (타임라인 뷰)")


class ScheduleCreate(Schedule):
    travel_id: int = Field(..., description="소속 여행 ID")


class ScheduleUpdate(BaseModel):
    day_number: Optional[int] = Field(None, ge=1)
    date: Optional[datetime.date] = None
    order_index: Optional[int] = Field(None, ge=0)
    place_name: Optional[str] = Field(None, max_length=100)
    place_address: Optional[str] = Field(None, max_length=255)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    category: Optional[ScheduleCategoryEnum] = None
    cost: Optional[int] = Field(None, ge=0)
    start_time: Optional[datetime.time] = None
    end_time: Optional[datetime.time] = None


class ScheduleSummaryResponse(Schedule):

    model_config = ConfigDict(from_attributes=True)

    id: int
    travel_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ScheduleDetailResponse(ScheduleSummaryResponse):
    memos: List["MemoResponse"] = []

ScheduleDetailResponse.model_rebuild()


class ScheduleMapPin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    day_number: int
    order_index: int
    place_name: str
    place_address: Optional[str]
    latitude: float
    longitude: float
    category: ScheduleCategoryEnum