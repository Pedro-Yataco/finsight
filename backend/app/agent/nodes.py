import json
import logging
from typing import Optional
from pydantic import BaseModel
from langchain_core.messages import AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from .state import AgentState
from .llm import get_llm
from .prompts import ROUTER_SYSTEM_PROMPT, RESPONDER_SYSTEM_PROMPT, SYNTHESIZER_PROMPT

logger = logging.getLogger(__name__)


class RouterOutput(BaseModel):
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    intent: str


def _parse_tool_output(data) -> dict:
    """Normalize MCP tool output to a plain dict.

    langchain-mcp-adapters returns list[TextContent] — each item has a .text
    attribute containing the JSON-serialized return value of the Python tool.
    """
    if isinstance(data, dict):
        return data
    if isinstance(data, list) and data:
        first = data[0]
        text = getattr(first, "text", None) or (first.get("text") if isinstance(first, dict) else None)
        if text:
            try:
                parsed = json.loads(text)
                return parsed if isinstance(parsed, dict) else {"value": parsed}
            except (json.JSONDecodeError, ValueError):
                return {"text": text}
    if isinstance(data, str):
        try:
            parsed = json.loads(data)
            return parsed if isinstance(parsed, dict) else {"value": parsed}
        except (json.JSONDecodeError, ValueError):
            return {"text": data}
    return {"error": f"Unrecognized tool output: {type(data).__name__}"}


def _safe_pct(value) -> float | None:
    try:
        f = float(value)
        return round(f * 100, 2) if f == f else None  # NaN check
    except (TypeError, ValueError):
        return None


def _cagr(start, end, years) -> float | None:
    try:
        s, e = float(start), float(end)
        if s <= 0 or e <= 0 or years <= 0:
            return None
        return round(((e / s) ** (1 / years) - 1) * 100, 2)
    except (TypeError, ValueError, ZeroDivisionError):
        return None


async def router_node(state: AgentState) -> dict:
    llm = get_llm()
    structured_llm = llm.with_structured_output(RouterOutput)
    messages = [SystemMessage(content=ROUTER_SYSTEM_PROMPT)] + list(state["messages"])
    result: RouterOutput = await structured_llm.ainvoke(messages)
    logger.info("[router] ticker=%s intent=%s", result.ticker, result.intent)
    return {"ticker": result.ticker, "company_name": result.company_name}


async def fetcher_node(state: AgentState, tools: list[BaseTool]) -> dict:
    ticker = state["ticker"]
    if not ticker:
        return {"raw_data": {}}

    tool_map = {tool.name: tool for tool in tools}
    raw_data: dict = {}

    for tool_name, key in [
        ("get_company_info", "company"),
        ("get_financials", "financials"),
        ("get_key_metrics", "key_metrics"),
        ("get_price_history", "price_history"),
    ]:
        if tool_name in tool_map:
            try:
                logger.info("[fetcher] calling %s(%s)", tool_name, ticker)
                data = await tool_map[tool_name].ainvoke({"ticker": ticker})
                raw_data[key] = _parse_tool_output(data)
                logger.info("[fetcher] %s → ok (keys: %s)", tool_name, list(raw_data[key].keys()))
            except Exception as e:
                logger.error("[fetcher] %s → error: %s", tool_name, e)
                raw_data[key] = {"error": str(e)}

    return {"raw_data": raw_data}


async def analyzer_node(state: AgentState) -> dict:
    raw = state.get("raw_data") or {}
    fin = raw.get("financials", {})
    price = raw.get("price_history", {})
    km = raw.get("key_metrics", {})

    derived: dict = {}

    # Revenue CAGR (uses up to 4 years of history)
    rev_hist = fin.get("revenue_history", {})
    if rev_hist and len(rev_hist) >= 2:
        years_sorted = sorted(rev_hist.keys(), reverse=True)  # most recent first
        oldest, newest = years_sorted[-1], years_sorted[0]
        n = len(years_sorted) - 1
        cagr = _cagr(rev_hist.get(oldest), rev_hist.get(newest), n)
        if cagr is not None:
            derived["revenue_cagr_pct"] = cagr

    # 3-year price CAGR
    p3y = price.get("price_3y_ago")
    p_now = price.get("current_price")
    if p3y and p_now:
        cagr = _cagr(p3y, p_now, 3)
        if cagr is not None:
            derived["price_cagr_3y_pct"] = cagr

    # 1-year price return
    p1y = price.get("price_1y_ago")
    if p1y and p_now:
        try:
            derived["price_return_1y_pct"] = round((float(p_now) / float(p1y) - 1) * 100, 2)
        except (TypeError, ValueError, ZeroDivisionError):
            pass

    # Margins as percentages (yfinance returns decimals, e.g. 0.43 = 43%)
    for src_key, dst_key in [
        ("gross_margins", "gross_margin_pct"),
        ("operating_margins", "operating_margin_pct"),
        ("profit_margins", "net_margin_pct"),
    ]:
        pct = _safe_pct(fin.get(src_key))
        if pct is not None:
            derived[dst_key] = pct

    # Net debt = total debt - cash
    debt = fin.get("total_debt")
    cash = fin.get("cash_and_equivalents")
    if debt is not None and cash is not None:
        try:
            derived["net_debt"] = int(float(debt) - float(cash))
        except (TypeError, ValueError):
            pass

    # FCF yield = FCF / market cap
    fcf = fin.get("free_cashflow")
    mkt_cap = km.get("market_cap")
    if fcf and mkt_cap:
        try:
            mc = float(mkt_cap)
            if mc > 0:
                derived["fcf_yield_pct"] = round(float(fcf) / mc * 100, 2)
        except (TypeError, ValueError):
            pass

    # ROE and ROA as percentages
    for src_key, dst_key in [("roe", "roe_pct"), ("roa", "roa_pct")]:
        pct = _safe_pct(km.get(src_key))
        if pct is not None:
            derived[dst_key] = pct

    logger.info("[analyzer] derived_metrics keys: %s", list(derived.keys()))
    return {"derived_metrics": derived}


async def synthesizer_node(state: AgentState) -> dict:
    llm = get_llm()

    company_name = (
        state.get("company_name")
        or (state.get("raw_data") or {}).get("company", {}).get("name", "Unknown")
    )
    ticker = state.get("ticker") or ""

    # Trim description to reduce prompt size (longBusinessSummary can be 500+ tokens)
    raw = (state.get("raw_data") or {}).copy()
    company = raw.get("company")
    if isinstance(company, dict) and isinstance(company.get("description"), str):
        desc = company["description"]
        if len(desc) > 400:
            raw = {**raw, "company": {**company, "description": desc[:400] + "..."}}

    logger.info("[synthesizer] generating report for %s (%s)", company_name, ticker)
    prompt = SYNTHESIZER_PROMPT.format(
        company_name=company_name,
        ticker=ticker,
        raw_data=json.dumps(raw, indent=2, ensure_ascii=False),
        derived_metrics=json.dumps(state.get("derived_metrics") or {}, indent=2, ensure_ascii=False),
    )

    response = await llm.ainvoke([SystemMessage(content=prompt)])
    updated_messages = list(state["messages"]) + [AIMessage(content=response.content)]
    return {"messages": updated_messages, "analysis_complete": True}


async def responder_node(state: AgentState) -> dict:
    """Handles non-finance queries — politely redirects the user."""
    llm = get_llm()
    response = await llm.ainvoke(
        [SystemMessage(content=RESPONDER_SYSTEM_PROMPT)] + list(state["messages"])
    )
    updated_messages = list(state["messages"]) + [AIMessage(content=response.content)]
    return {"messages": updated_messages, "analysis_complete": True}
