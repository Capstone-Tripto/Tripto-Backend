from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.schemas import ScheduleCreate, ScheduleUpdate, ScheduleSummaryResponse, ScheduleDetailResponse, ScheduleMapPin
from app.services import schedule_service

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.post("", response_model=ScheduleSummaryResponse, status_code=201)
async def create_schedule(
    data: ScheduleCreate, db: AsyncSession = Depends(get_async_db)
):
    return await schedule_service.create_schedule(db, data)


@router.get("/{schedule_id}", response_model=ScheduleDetailResponse)
async def get_schedule(schedule_id: int, db: AsyncSession = Depends(get_async_db)):
    schedule = await schedule_service.get_schedule(db, schedule_id)
    if not schedule:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")
    return schedule


@router.patch("/{schedule_id}", response_model=ScheduleSummaryResponse)
async def update_schedule(
    schedule_id: int,
    data: ScheduleUpdate,
    db: AsyncSession = Depends(get_async_db),
):
    schedule = await schedule_service.update_schedule(db, schedule_id, data)
    if not schedule:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")
    return schedule


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(schedule_id: int, db: AsyncSession = Depends(get_async_db)):
    deleted = await schedule_service.delete_schedule(db, schedule_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")


@router.get("/travel/{travel_id}", response_model=List[ScheduleSummaryResponse])
async def list_schedules(travel_id: int, db: AsyncSession = Depends(get_async_db)):
    return await schedule_service.get_schedules_by_travel(db, travel_id)


@router.get("/travel/{travel_id}/map-pins", response_model=List[ScheduleMapPin])
async def get_map_pins(travel_id: int, db: AsyncSession = Depends(get_async_db)):
    return await schedule_service.get_map_pins(db, travel_id)