from typing import Annotated, List, TypedDict, Optional
from langgraph.graph import add_messages, MessagesState
from langchain_core.messages import BaseMessage

class InputState(TypedDict):
    """1. 입력 스키마"""
    question : str


class TravelState(MessagesState):
    """2. 대화 관리(private)"""
    user_name : str                 # user의 닉네임
    user_id = str                   # 대화 아이디
    destination: Optional[str]      # 목적지 (예: 제주도, 파리)
    traveldates: Optional[dict]    # 여행 일정 (예: {"start": "2024-05-01", "end": "2024-05-05"})
    budget: Optional[int]           # 예산 범위
    preferences: List[str]          # 선호도 (예: ["자연", "맛집", "쇼핑"])
    current_step: str               # 현재 대화 단계 (예: "planning", "booking", "completed")
    itinerary: List[str]            # 확정된 일정 리스트



class OutputState(TypedDict):
    """3. 출력 스키마"""
    answer: str

