# FinSight — Technical Architecture

## System Overview

FinSight is a conversational AI agent that performs fundamental financial analysis of publicly traded companies. The user types a company name or question in natural language; the agent retrieves real financial data via MCP tools, computes derived metrics, and returns a structured Markdown analysis report.

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│                   Next.js 14 + TypeScript                    │
│                    Deployed on Vercel (free)                  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Chat Interface                                        │  │
│  │  · MessageList  (react-markdown rendering)             │  │
│  │  · MessageBubble (user vs. agent bubbles)              │  │
│  │  · InputBar     (free-text input + send)               │  │
│  │  · LoadingSpinner while agent runs                     │  │
│  └────────────────────────┬───────────────────────────────┘  │
└───────────────────────────┼──────────────────────────────────┘
                            │ POST /api/chat
                            │ { messages: Message[] }
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                          BACKEND                             │
│                    FastAPI + Python 3.12                     │
│                 Deployed on Render.com (free)                │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  POST /api/chat                                        │  │
│  │  · Validates request body                              │  │
│  │  · Invokes LangGraph agent                             │  │
│  │  · Returns { reply: string }                           │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │                                  │
│  ┌────────────────────────▼───────────────────────────────┐  │
│  │              LangGraph Agent                           │  │
│  │      Model: Gemini 1.5 Flash (LangChain abstracted)    │  │
│  │      Tracing: LangSmith (2 env vars, automatic)        │  │
│  │                                                        │  │
│  │  router ──► fetcher ──► analyzer ──► synthesizer       │  │
│  │     └──────────────────────────────► responder         │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │ MCP Protocol (stdio)             │
│  ┌────────────────────────▼───────────────────────────────┐  │
│  │              MCP Server (Python)                       │  │
│  │       Co-located with FastAPI on Render                │  │
│  │                                                        │  │
│  │  · get_company_info(ticker)                            │  │
│  │  · get_financials(ticker)                              │  │
│  │  · get_key_metrics(ticker)                             │  │
│  │  · get_price_history(ticker, period)                   │  │
│  └────────────────────────┬───────────────────────────────┘  │
│                           │ Python library call              │
│  ┌────────────────────────▼───────────────────────────────┐  │
│  │                    yfinance                            │  │
│  │           (Yahoo Finance — no API key needed)          │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## LangGraph Agent: Node-by-Node

### State

```python
class AgentState(TypedDict):
    messages: list[BaseMessage]   # full conversation history sent from frontend
    ticker: str | None            # resolved stock ticker, e.g. "AAPL"
    company_name: str | None      # human-readable name, e.g. "Apple Inc."
    raw_data: dict | None         # data returned by MCP tools
    derived_metrics: dict | None  # computed ratios (CAGR, margins, etc.)
    analysis_complete: bool
```

### Nodes

| Node | Calls LLM | Responsibility |
|------|-----------|---------------|
| `router` | Yes | Classify intent; extract ticker/company from user message |
| `fetcher` | No | Call all 4 MCP tools; aggregate raw financial data |
| `analyzer` | No | Compute derived metrics from raw data (Python math, no LLM) |
| `synthesizer` | Yes | Write the Markdown analysis report from processed data |
| `responder` | Yes | Handle out-of-scope queries, errors, or greetings gracefully |

### Graph Edges

```
START    → router
router   → fetcher      (if ticker extracted)
router   → responder    (if out-of-scope or greeting)
fetcher  → analyzer
analyzer → synthesizer
synthesizer → END
responder   → END
```

### Conditional Edge Logic

```python
def should_analyze(state: AgentState) -> Literal["fetcher", "responder"]:
    return "fetcher" if state["ticker"] is not None else "responder"
```

---

## MCP Server: Tool Specifications

### `get_company_info(ticker: str) → dict`
```python
# Returns
{
    "name": str,
    "sector": str,
    "industry": str,
    "description": str,
    "country": str,
    "employees": int,
    "website": str
}
# Source: yfinance.Ticker(ticker).info
```

### `get_financials(ticker: str) → dict`
```python
# Returns (last 3 fiscal years, most recent first)
{
    "revenue":           [float, float, float],
    "net_income":        [float, float, float],
    "operating_income":  [float, float, float],
    "ebitda":            [float, float, float]
}
# Source: yfinance.Ticker(ticker).financials
```

### `get_key_metrics(ticker: str) → dict`
```python
# Returns
{
    "pe_ratio":       float | None,
    "pb_ratio":       float | None,
    "ev_ebitda":      float | None,
    "debt_to_equity": float | None,
    "current_ratio":  float | None,
    "roe":            float | None,
    "roa":            float | None,
    "profit_margin":  float | None
}
# Source: yfinance.Ticker(ticker).info
```

### `get_price_history(ticker: str, period: str = "1y") → dict`
```python
# Returns
{
    "current_price":  float,
    "price_52w_high": float,
    "price_52w_low":  float,
    "market_cap":     float,
    "beta":           float | None,
    "avg_volume":     int
}
# Source: yfinance.Ticker(ticker).history(period=period)
```

---

## Provider Abstraction Pattern

Switching LLM providers requires changing one environment variable. Zero changes to agent code.

```python
# backend/app/agent/llm.py

def get_llm() -> BaseChatModel:
    provider = os.getenv("LLM_PROVIDER", "gemini")

    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model="claude-haiku-4-5-20251001")

    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")

# Usage in every node that needs the LLM:
# llm = get_llm()
# response = llm.invoke(messages)
```

---

## LangSmith Integration

Two environment variables enable full observability. No other code required — LangGraph reports automatically.

```bash
# backend/.env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls_...        # from smith.langchain.com (free tier)
LANGCHAIN_PROJECT=finsight
```

Every node execution, tool call, LLM invocation, and token count appears as a trace in the LangSmith dashboard.

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LLM | Gemini 1.5 Flash | Free tier, sufficient quality for structured financial text |
| LLM abstraction | LangChain `BaseChatModel` | One env var to switch to Claude or GPT-4 |
| Agent framework | LangGraph | Stateful graph → debuggable, extensible, industry-standard |
| Data source | yfinance | No API key, covers MVP fundamentals |
| MCP placement | Co-located with FastAPI on Render | Avoids network latency; simpler free-tier ops |
| Persistence | Stateless MVP | Eliminates DB dependency; frontend sends full `messages[]` per request |
| Deployment | Vercel + Render | Both free tiers, sufficient for demo |
| Observability | LangSmith | 2-line integration, free tier, traces every agent call |
| Output format | Markdown (MVP) | Rendered client-side via react-markdown; no extra backend work |

---

## Post-MVP Extensions

| Feature | What to add |
|---------|-------------|
| Chat history | Supabase PostgreSQL + session ID in API request |
| PDF export | `WeasyPrint` or `reportlab` endpoint in FastAPI |
| News context | NewsAPI → new MCP tool `get_recent_news(ticker)` |
| SEC filings | EDGAR API → new MCP tool `get_sec_filing(ticker)` |
| Structured output | LangChain structured output parser + Recharts in frontend |
| Multi-company comparison | New `compare_node` in LangGraph graph |
