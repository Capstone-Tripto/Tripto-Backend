from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.schemas import TravelCreate, TravelUpdate, TravelResponse, TravelDetailResponse
from app.schemas.schedule_schema import ScheduleMapPin
from app.services import travel_service, schedule_service

router = APIRouter(prefix="/travels", tags=["travels"])


@router.post("", response_model=TravelResponse, status_code=201)
async def create_travel(
    data: TravelCreate,
    owner_id: int = Query(..., description="여행 소유자 ID (로그인 연동 전)"),
    db: AsyncSession = Depends(get_async_db),
):
    return await travel_service.create_travel(db, data, owner_id)


@router.get("/{travel_id}", response_model=TravelDetailResponse)
async def get_travel(travel_id: int, db: AsyncSession = Depends(get_async_db)):
    travel = await travel_service.get_travel(db, travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="여행을 찾을 수 없습니다.")
    return travel


@router.patch("/{travel_id}", response_model=TravelResponse)
async def update_travel(
    travel_id: int,
    data: TravelUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    travel = await travel_service.update_travel(db, travel_id, data)
    if not travel:
        raise HTTPException(status_code=404, detail="여행을 찾을 수 없습니다.")
    return travel


@router.delete("/{travel_id}", status_code=204)
async def delete_travel(travel_id: int, db: AsyncSession = Depends(get_async_db)):
    deleted = await travel_service.delete_travel(db, travel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="여행을 찾을 수 없습니다.")


@router.get("", response_model=List[TravelResponse])
async def list_travels(
    owner_id: int = Query(..., description="여행 소유자 ID(로그인 연동 전)"),
    db: AsyncSession = Depends(get_async_db),
):
    return await travel_service.get_travels_by_owner(db, owner_id)

@router.get("/{travel_id}/map", response_model=List[ScheduleMapPin])
async def get_map_pins(travel_id: int, db: AsyncSession = Depends(get_async_db)):
    travel = await travel_service.get_travel(db, travel_id)
    if not travel:
        raise HTTPException(status_code=404, detail="여행을 찾을 수 없습니다.")
    return await schedule_service.get_map_pins(db, travel_id)