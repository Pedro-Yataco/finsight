from functools import partial
from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.tools import BaseTool
from .state import AgentState
from .nodes import router_node, fetcher_node, responder_node


def _route(state: AgentState) -> Literal["fetcher", "responder"]:
    return "fetcher" if state.get("ticker") else "responder"


def create_graph(tools: list[BaseTool]):
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("fetcher", partial(fetcher_node, tools=tools))
    graph.add_node("responder", responder_node)

    graph.set_entry_point("router")
    graph.add_conditional_edges("router", _route, {
        "fetcher": "fetcher",
        "responder": "responder",
    })
    graph.add_edge("fetcher", "responder")
    graph.add_edge("responder", END)

    return graph.compile()
