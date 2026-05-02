from typing import TypedDict
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    messages: list[BaseMessage]
    ticker: str | None
    company_name: str | None
    raw_data: dict | None
    derived_metrics: dict | None
    analysis_complete: bool
