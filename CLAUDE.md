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