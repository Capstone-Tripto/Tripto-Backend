from langchain_core.messages import AIMessage
from state import InputState, TravelState, OutputState


REQUIRED_FIELDS = {
    "destination": "어디로 떠나고 싶으신가요? (예시: 제주도, 경주)",
    "travel_dates": "여행 일정은 언제인가요? 구체적인 날짜나 기간을 알려주세요.",
    "budget": "예산은 어느 정도로 생각하시나요? (예시: 100만원 이내)"
}

def Info_Gatherer(state: TravelState) -> dict:
    """필수 정보가 빠졌을 때 사용자에게 질문 던짐"""

    missing_info_question = []

    for field, question in REQUIRED_FIELDS.items():
        val = state.get(field, None)

        if not val or val == "NULL":
            missing_info_question.append(question)

    if missing_info_question:
        target_question = missing_info_question[0]

        return {
            "messages": state["messages"] + [
                AIMessage(content=f"여행 계획을 위해 몇가지 정보가 더 필요합니다. {target_question}")
            ],
            "current_step": "asking_info"
        }

    return {
        "current_step": "info_gathered"
    }

