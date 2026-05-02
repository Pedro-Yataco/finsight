# FinSight — Architecture Decision Records

ADR format: **Context → Decision → Consequences**

---

## ADR-001: LLM Provider Abstraction via Factory Function

**Date:** 2026-05-01
**Status:** Accepted

**Context:**
The project requires a free LLM for development. Multiple providers exist (Gemini, Claude, Ollama, Groq) with different APIs, pricing, and rate limits. Hard-coding a provider would make future switches expensive.

**Decision:**
Centralize all LLM instantiation in `backend/app/agent/llm.py` via a `get_llm()` factory. Provider is selected by the `LLM_PROVIDER` environment variable. Each provider branch is lazy-imported so unused providers don't need to be installed.

**Provider ladder (current):**
- `ollama` → local dev, zero cost, zero rate limits (`qwen2.5:7b`)
- `groq` → cloud deploy, free tier, fast (`llama-3.3-70b-versatile`)
- `gemini` → free tier with strict rate limits (`gemini-2.0-flash`)
- `anthropic` → paid, highest quality

**Consequences:**
- ✅ Switching provider = one env var change, zero code changes
- ✅ All providers share the same `BaseChatModel` interface
- ⚠️ Structured output reliability varies by model — test after every provider switch

---

## ADR-002: Ollama as Primary Development Provider

**Date:** 2026-05-01
**Status:** Accepted

**Context:**
Gemini 1.5 Flash was the original plan, but two blockers emerged during Week 1:
1. `gemini-1.5-flash` was deprecated (replaced by `gemini-2.0-flash`)
2. The free tier rate limit was exhausted with a single test request at the current usage level

**Decision:**
Switch primary development provider to local Ollama with `qwen2.5:7b`. This model is already downloaded, runs offline, has no rate limits, and supports tool calling (required for `with_structured_output()`).

For cloud deployment (Render.com, Semana 5): use Groq free tier, which has generous daily limits and requires no credit card.

**Consequences:**
- ✅ Zero cost, zero rate limits during development
- ✅ Works offline
- ⚠️ `qwen2.5:7b` is less capable than `gemini-2.0-flash` — analysis quality will improve on deploy
- ⚠️ Ollama must be running locally (`ollama serve`) before starting uvicorn

---

## ADR-003: MCP Client Lifecycle via `client.session()` Context Manager

**Date:** 2026-05-01
**Status:** Accepted

**Context:**
`langchain-mcp-adapters` 0.1.0 removed `async with MultiServerMCPClient(...)` (context manager on the client itself). Using it caused a `NotImplementedError` on FastAPI startup.

**Decision:**
Use `client.session(server_name)` as the async context manager instead, combined with `load_mcp_tools(session)`. This is wrapped inside FastAPI's `lifespan` context manager so the MCP subprocess stays alive for the entire app lifetime.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    client = create_mcp_client()
    async with client.session(MCP_SERVER_NAME) as session:
        tools = await load_mcp_tools(session)
        app.state.graph = create_graph(tools)
        yield  # MCP subprocess lives here
```

**Consequences:**
- ✅ MCP subprocess is alive for the full app lifetime — tools are always callable
- ✅ Clean shutdown: session closes when app stops
- ⚠️ If the MCP subprocess crashes, FastAPI must restart to reconnect

---

## ADR-004: `load_dotenv()` Before Framework Initialization

**Date:** 2026-05-01
**Status:** Accepted

**Context:**
`pydantic-settings` reads `.env` into the `Settings` Python object but does **not** populate `os.environ`. LangChain providers (e.g., `ChatGoogleGenerativeAI`) read API keys directly from `os.environ`, not from our `settings` object. This caused a `ValidationError: API key required` even with a valid `.env`.

**Decision:**
Call `load_dotenv()` as the first statement in `app/main.py`, before any LangChain import or framework initialization. This loads the `.env` file into `os.environ`, making keys available to all libraries.

```python
from dotenv import load_dotenv
load_dotenv()  # must be first — before LangChain imports

from contextlib import asynccontextmanager
from fastapi import FastAPI
...
```

**Consequences:**
- ✅ All LLM providers find their API keys via `os.environ`
- ✅ `pydantic-settings` and `load_dotenv()` both read from the same `.env` file without conflict
- ⚠️ On production (Render), env vars are set via the platform UI — `load_dotenv()` finds no file and does nothing, which is correct

---

## ADR-005: MCP Server PYTHONPATH Injection

**Date:** 2026-05-01
**Status:** Accepted

**Context:**
The MCP Server runs as a subprocess started by `MultiServerMCPClient`. It needs to import `app.mcp.tools.company` (i.e., the `backend/` directory must be in its Python path). The subprocess does not inherit `sys.path` from the parent process — only `PYTHONPATH` env var is inherited.

**Decision:**
In `mcp/client.py`, dynamically compute the `backend/` directory path and inject it into the subprocess's `PYTHONPATH` via the `env` parameter:

```python
_BACKEND_DIR = str(Path(__file__).resolve().parent.parent.parent)

env = os.environ.copy()
env["PYTHONPATH"] = _BACKEND_DIR + os.pathsep + env.get("PYTHONPATH", "")
```

**Consequences:**
- ✅ MCP subprocess can always import `app.*` regardless of where uvicorn was started from
- ✅ Works on both local dev and Render production (Render sets WORKDIR, subprocess inherits env)
- ✅ No need to `cd backend/` before starting uvicorn
