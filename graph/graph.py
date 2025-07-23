from langgraph.graph import StateGraph
from graph.state import ChatState
from graph.nodes import node_run_agent

graph = StateGraph(ChatState)

graph.add_node("run_agent", node_run_agent)
graph.set_entry_point("run_agent")
graph.set_finish_point("run_agent")

app = graph.compile()
