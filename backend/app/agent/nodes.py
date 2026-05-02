import json
from typing import Optional
from pydantic import BaseModel
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from .state import AgentState
from .llm import get_llm
from .prompts import ROUTER_SYSTEM_PROMPT, RESPONDER_SYSTEM_PROMPT, COMPANY_OVERVIEW_PROMPT


class RouterOutput(BaseModel):
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    intent: str


async def router_node(state: AgentState) -> dict:
    llm = get_llm()
    structured_llm = llm.with_structured_output(RouterOutput)
    messages = [SystemMessage(content=ROUTER_SYSTEM_PROMPT)] + list(state["messages"])
    result: RouterOutput = await structured_llm.ainvoke(messages)
    return {"ticker": result.ticker, "company_name": result.company_name}


async def fetcher_node(state: AgentState, tools: list[BaseTool]) -> dict:
    ticker = state["ticker"]
    if not ticker:
        return {"raw_data": {}}

    tool_map = {tool.name: tool for tool in tools}
    raw_data: dict = {}

    if "get_company_info" in tool_map:
        data = await tool_map["get_company_info"].ainvoke({"ticker": ticker})
        raw_data["company"] = data

    return {"raw_data": raw_data}


async def responder_node(state: AgentState) -> dict:
    llm = get_llm()

    if state.get("raw_data"):
        prompt = COMPANY_OVERVIEW_PROMPT.format(
            company_data=json.dumps(state["raw_data"], indent=2, ensure_ascii=False)
        )
        response = await llm.ainvoke(
            [SystemMessage(content=prompt)] + list(state["messages"])
        )
    else:
        response = await llm.ainvoke(
            [SystemMessage(content=RESPONDER_SYSTEM_PROMPT)] + list(state["messages"])
        )

    updated_messages = list(state["messages"]) + [AIMessage(content=response.content)]
    return {"messages": updated_messages, "analysis_complete": True}
