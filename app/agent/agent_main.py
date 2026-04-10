from nodes.Intent_Analyzer import Intent_Analyzer
from nodes.Info_Gatherer import Info_Gatherer

def main():
    from langchain_core.messages import HumanMessage

    q1 = input("입력: ")

    state = {
        "question": [q1],
        "messages": [HumanMessage(content=q1)],
        "destination": None,
        "traveldates": None,
        "budget": None,
        "preferences": [],
        "current_step": None
    }

    # Intent 분석
    res1 = Intent_Analyzer(state)
    state.update(res1)

    # Info Gather
    res2 = Info_Gatherer(state)
    state.update(res2)

    print("\n=== 최종 상태 ===")
    print(f"{state['question']} \n")
    print(f"{state['messages']} \n")
    print(f"{state['destination']} \n")
    print(f"{state['traveldates']} \n")
    print(f"{state['budget']} \n")
    print(f"{state['preferences']} \n")
    print(f"{state['current_step']} \n")

    if "messages" in state:
        print("\n=== 챗봇 응답 ===")
        print(state["messages"][-1].content)


if __name__ == "__main__":
    main()