from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.travel_model import Travel
from app.schemas.travel_schema import TravelCreate, TravelUpdate


async def create_travel(db: AsyncSession, data: TravelCreate, owner_id: int) -> Travel:
    travel = Travel(**data.model_dump(), owner_id=owner_id)
    db.add(travel)
    await db.commit()
    await db.refresh(travel)
    return travel


async def get_travel(db: AsyncSession, travel_id: int) -> Optional[Travel]:
    result = await db.execute(select(Travel).where(Travel.id == travel_id))
    return result.scalar_one_or_none()


async def get_travels_by_owner(db: AsyncSession, owner_id: int) -> List[Travel]:
    result = await db.execute(select(Travel).where(Travel.owner_id == owner_id))
    return list(result.scalars().all())


async def update_travel(
    db: AsyncSession, travel_id: int, data: TravelUpdate
) -> Optional[Travel]:
    travel = await get_travel(db, travel_id)
    if not travel:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(travel, field, value)
    await db.commit()
    await db.refresh(travel)
    return travel


async def delete_travel(db: AsyncSession, travel_id: int) -> bool:
    travel = await get_travel(db, travel_id)
    if not travel:
        return False
    await db.delete(travel)
    await db.commit()
    return True