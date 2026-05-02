# FinSight — Claude Code Instructions

## Project
Conversational AI agent for fundamental stock analysis.
Stack: LangGraph + Ollama/Groq/Gemini (switchable) + MCP + FastAPI + Next.js

## Key commands
- Backend dev:  cd backend && uvicorn app.main:app --reload --port 8000
- Frontend dev: cd frontend && npm run dev
- Tests:        cd backend && pytest
- Full stack:   docker-compose up
- NOTE: Do NOT run `python -m app.mcp.server` directly — it is started automatically by FastAPI on startup

## LLM providers (switch via LLM_PROVIDER env var)
- ollama  → local dev, no rate limits, requires `ollama serve` running
- groq    → cloud deploy, free tier (console.groq.com), requires GROQ_API_KEY
- gemini  → free tier with strict rate limits, requires GEMINI_API_KEY
- All providers use the same BaseChatModel interface — zero code changes to switch

## Important files
- Agent graph:    backend/app/agent/graph.py
- Agent nodes:    backend/app/agent/nodes.py
- LLM factory:    backend/app/agent/llm.py
- System prompts: backend/app/agent/prompts.py
- MCP tools:      backend/app/mcp/tools/
- MCP client:     backend/app/mcp/client.py
- API route:      backend/app/routes/chat.py
- ADRs:           docs/decisions.md

## Conventions
- System prompts live in prompts.py, never inline inside node functions
- MCP tools are tested individually (test_mcp_tools.py) before agent integration
- Every PR gets a semver tag before merging to main
- LLM provider is switched via LLM_PROVIDER env var — never hardcode the provider
- load_dotenv() must be the first statement in main.py (pydantic-settings does not populate os.environ)