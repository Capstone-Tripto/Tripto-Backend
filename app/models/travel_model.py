from sqlalchemy import Boolean, Column, Date, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Travel(Base, TimestampMixin):

    __tablename__ = "travels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, nullable=False, index=True)
    title = Column(String(100), nullable=False, comment="여행 제목")
    destination = Column(String(100), nullable=False, comment="목적지 (예: 제주도, 파리)")
    start_date = Column(Date, nullable=False, comment="여행 시작일")
    end_date = Column(Date, nullable=False, comment="여행 종료일")

    # Relationships
    schedules = relationship(
        "Schedule",
        back_populates="travel",
        cascade="all, delete-orphan",
        order_by="Schedule.day_number, Schedule.order_index",
    )