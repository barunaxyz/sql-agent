from agent.agent import ask_agent
from langchain_core.messages import HumanMessage, AIMessage

def node_run_agent(state):
    result = ask_agent(state["user_input"], state["messages"])
    state["messages"].append(HumanMessage(content=state["user_input"]))
    state["messages"].append(AIMessage(content=result.get("output")))
    state["answer"] = result.get("output")
    return state