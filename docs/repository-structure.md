# FinSight — Repository Structure

## Full Folder Tree

```
finsight/
│
├── .github/
│   └── workflows/
│       └── ci.yml                      # Run backend tests on every push to main
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI app creation + route registration
│   │   ├── config.py                   # Settings via pydantic-settings (reads .env)
│   │   │
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── chat.py                 # POST /api/chat handler
│   │   │
│   │   ├── agent/
│   │   │   ├── __init__.py
│   │   │   ├── graph.py                # LangGraph StateGraph definition + compilation
│   │   │   ├── nodes.py                # Node functions: router, fetcher, analyzer, synthesizer, responder
│   │   │   ├── state.py                # AgentState TypedDict
│   │   │   ├── prompts.py              # System prompts (version-controlled, never inline)
│   │   │   └── llm.py                  # get_llm() factory — provider abstraction
│   │   │
│   │   └── mcp/
│   │       ├── __init__.py
│   │       ├── server.py               # MCP Server entry point (run as subprocess)
│   │       ├── client.py               # MCP Client setup using langchain-mcp-adapters
│   │       └── tools/
│   │           ├── __init__.py
│   │           ├── company.py          # get_company_info()
│   │           ├── financials.py       # get_financials()
│   │           ├── metrics.py          # get_key_metrics()
│   │           └── prices.py           # get_price_history()
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py                 # Shared fixtures (test client, env override)
│   │   ├── test_mcp_tools.py           # Test each MCP tool against real tickers
│   │   └── test_agent.py              # E2E test: full agent invocation
│   │
│   ├── Dockerfile                      # Production image: FastAPI + MCP Server
│   ├── pyproject.toml                  # Dependencies + project metadata (PEP 517)
│   ├── .env.example                    # Template — no real secrets committed
│   └── .python-version                 # Pin to 3.12
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx              # Root layout (fonts, metadata, dark mode class)
│   │   │   ├── page.tsx                # Root page → renders <ChatContainer />
│   │   │   └── globals.css
│   │   │
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   │   ├── ChatContainer.tsx   # Owns messages state, handles API calls
│   │   │   │   ├── MessageList.tsx     # Scrollable list, auto-scrolls to latest
│   │   │   │   ├── MessageBubble.tsx   # User vs. agent bubble + react-markdown
│   │   │   │   └── InputBar.tsx        # Text input + send button + Enter key
│   │   │   └── ui/
│   │   │       ├── LoadingSpinner.tsx
│   │   │       └── ErrorBanner.tsx
│   │   │
│   │   ├── lib/
│   │   │   └── api.ts                  # fetch wrapper for POST /api/chat
│   │   │
│   │   └── types/
│   │       └── chat.ts                 # Message, ChatRequest, ChatResponse types
│   │
│   ├── public/
│   │   └── favicon.ico
│   ├── next.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── .env.example                    # NEXT_PUBLIC_API_URL=http://localhost:8000
│
├── docs/
│   ├── architecture.md                 # System architecture (this project's sibling)
│   ├── decisions.md                    # Architecture Decision Records (ADRs)
│   ├── roadmap.md                      # 6-week development plan
│   └── api.md                          # FastAPI endpoint reference
│
├── docker-compose.yml                  # Local dev: backend (FastAPI + MCP Server)
├── .env.example                        # Root-level: documents all required env vars
├── .gitignore
├── CLAUDE.md                           # Instructions for Claude Code (auto-read each session)
└── README.md
```

---

## Files to Create on Day 1

The minimum needed to have a working skeleton committed:

```
finsight/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI with GET /health
│   │   ├── config.py        # pydantic-settings: GEMINI_API_KEY, LLM_PROVIDER
│   │   └── mcp/
│   │       ├── server.py    # MCP Server entry point (stub)
│   │       └── tools/
│   │           └── company.py   # get_company_info() — first real tool
│   ├── pyproject.toml
│   └── .env.example
├── docker-compose.yml
├── .gitignore
├── CLAUDE.md
└── README.md                # Title + one-paragraph description + "In progress"
```

---

## Naming Conventions

| Entity | Convention | Example |
|--------|-----------|---------|
| Python files | `snake_case` | `agent_state.py` |
| Python classes | `PascalCase` | `AgentState` |
| Python functions | `snake_case` | `get_company_info()` |
| TypeScript component files | `PascalCase` | `MessageBubble.tsx` |
| TypeScript utility files | `camelCase` | `api.ts` |
| TypeScript types/interfaces | `PascalCase` | `ChatRequest` |
| Environment variables | `SCREAMING_SNAKE_CASE` | `GEMINI_API_KEY` |
| Git branches | `kebab-case` | `feature/fetcher-node` |
| Git tags | `semver` | `v0.2-agent` |

---

## Key Dependencies

### Backend — `pyproject.toml`

```toml
[project]
name = "finsight-backend"
version = "0.1.0"
requires-python = ">=3.12"

dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "langgraph>=0.2.0",
    "langchain>=0.3.0",
    "langchain-google-genai>=2.0.0",
    "langchain-mcp-adapters>=0.1.0",
    "mcp>=1.0.0",
    "yfinance>=0.2.40",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.28.0",
]
```

### Frontend — `package.json`

```json
{
  "dependencies": {
    "next": "14.x",
    "react": "18.x",
    "react-dom": "18.x",
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0"
  },
  "devDependencies": {
    "typescript": "^5",
    "@types/node": "^20",
    "@types/react": "^18",
    "tailwindcss": "^3",
    "autoprefixer": "^10",
    "postcss": "^8"
  }
}
```

---

## Environment Variables Reference

```bash
# backend/.env.example

# LLM Provider (switch with one variable — no code changes)
LLM_PROVIDER=gemini                          # or "anthropic"
GEMINI_API_KEY=AIza...                       # from Google AI Studio (free)
# ANTHROPIC_API_KEY=sk-ant-...              # only needed if LLM_PROVIDER=anthropic

# Observability (2 lines = full LangSmith tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls_...                     # from smith.langchain.com (free tier)
LANGCHAIN_PROJECT=finsight

# App
PORT=8000
ENVIRONMENT=development                      # or "production"
ALLOWED_ORIGINS=http://localhost:3000        # comma-separated list

# frontend/.env.example
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## `.gitignore` (root)

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
dist/
.pytest_cache/

# Node
node_modules/
.next/
out/

# Environment
.env
.env.local
.env.*.local

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
```

---

## `CLAUDE.md` (root) — Template for Day 1

```markdown
# FinSight — Claude Code Instructions

## Project
Conversational AI agent for fundamental stock analysis.
Stack: LangGraph + Gemini Flash + MCP + FastAPI + Next.js

## Key commands
- Backend dev:  cd backend && uvicorn app.main:app --reload --port 8000
- MCP Server:   cd backend && python -m app.mcp.server
- Frontend dev: cd frontend && npm run dev
- Tests:        cd backend && pytest
- Full stack:   docker-compose up

## Important files
- Agent graph:    backend/app/agent/graph.py
- Agent nodes:    backend/app/agent/nodes.py
- LLM factory:    backend/app/agent/llm.py
- System prompts: backend/app/agent/prompts.py
- MCP tools:      backend/app/mcp/tools/
- API route:      backend/app/routes/chat.py

## Conventions
- System prompts live in prompts.py, never inline inside node functions
- MCP tools are tested individually (test_mcp_tools.py) before agent integration
- Every PR gets a semver tag before merging to main
- LLM provider is switched via LLM_PROVIDER env var — never hardcode the provider
```
