import os
from dotenv import load_dotenv

from state import InputState, TravelState, OutputState
from typing import Annotated, List, TypedDict, Optional
from pydantic import BaseModel, Field # Pydantic 모델 정의를 위해 필요
from langchain_core.messages import SystemMessage, HumanMessage

from langchain_google_genai import ChatGoogleGenerativeAI
from operator import add


load_dotenv()

class TravelInfo(BaseModel):
    destination : str
    traveldates : str
    budget : str
    preferences : Annotated[list[str], add]


def Intent_Analyzer(state:InputState) -> TravelState:
    '''사용자의 질문에서 목적지, 날짜, 취향 등을 추출하여 state 업데이트'''

    # 1. 모델 설정
    llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    structured_llm = llm.with_structured_output(TravelInfo)

    # 2. 프롬프트 구성 및 LLM 호출
    system_prompt = """
    너는 여행 전문가야.
    사용자의 문장에서 목적지, 여행일정(날짜), 예산, 선호하는 여행 스타일을 추출해
    해당하는 정보가 없다면 Null로 처리해
    """
    user_input = state['question']

    #LLM 실행
    extracted = structured_llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_input)
    ])

    # 3. 데이터 가공 및 반환
    return {
        "destination" : extracted.destination,
        "traveldates" : extracted.traveldates,
        "budget" : extracted.budget,
        "preferences" : extracted.preferences,
        "current_step" : "start"
    }
