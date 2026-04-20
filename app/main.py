from fastapi import FastAPI

from app.api import travel, schedule, memo

app = FastAPI()

app.include_router(travel.router, prefix="/api")
app.include_router(schedule.router, prefix="/api")
app.include_router(memo.router, prefix="/api")