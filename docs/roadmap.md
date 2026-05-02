# FinSight — 6-Week Development Roadmap

**Total budget:** 90 hours (15h/week × 6 weeks)
**Start date:** 2026-05-01
**Target completion:** 2026-06-12

---

## Phase Overview

| Phase | Week | Focus | End Deliverable | Status |
|-------|------|-------|-----------------|--------|
| 1 | 1 | Foundation | MCP Server running, LangGraph skeleton wired to 1 tool | ✅ Done |
| 2 | 2 | Core Agent | Agent produces a real analysis via curl | 🔄 Next |
| 3 | 3 | Frontend | Working chat UI in browser, connected to backend | — |
| 4 | 4 | QA & Polish | Edge cases handled, analysis quality improved | — |
| 5 | 5 | Deployment | Live on Vercel + Render with public URL | — |
| 6 | 6 | Portfolio Polish | README, ADRs, demo GIF, docs complete | — |

---

## Week 1 — Foundation (15h)

**Goal:** Monorepo scaffolded. MCP Server running with one real tool. LangGraph skeleton calls it.

| Task | Hours |
|------|-------|
| Monorepo setup: `backend/`, `frontend/`, `docker-compose.yml`, `.gitignore` | 1h |
| Backend: FastAPI skeleton + `GET /health` endpoint | 1.5h |
| Backend: `pyproject.toml` with all dependencies, virtual env | 1h |
| MCP Server: `server.py` + first tool `get_company_info()` | 3h |
| MCP Client: connect FastAPI to MCP Server via `langchain-mcp-adapters` | 2h |
| LangGraph: minimal 2-node graph (`router` → `responder`) — no tools yet | 2h |
| LangGraph: wire `get_company_info` as first MCP tool in `fetcher` node | 2h |
| Integration test: FastAPI calls agent calls MCP tool — verify data flows | 1.5h |
| GitHub: initial commit, README skeleton ("Work in progress"), `v0.1` tag | 1h |

**GitHub milestone:** `v0.1-foundation` — agent calls one MCP tool end-to-end.

---

## Week 2 — Core Agent (15h)

**Goal:** Full 4-tool MCP Server. Complete LangGraph graph. Agent produces a real analysis report.

| Task | Hours |
|------|-------|
| MCP Server: remaining 3 tools (`get_financials`, `get_key_metrics`, `get_price_history`) | 4h |
| LangGraph: `fetcher` node calling all 4 tools and aggregating `raw_data` | 2h |
| LangGraph: `analyzer` node computing derived metrics (CAGR, margin trends) | 2h |
| LangGraph: `synthesizer` node — write system prompt, generate Markdown report | 2.5h |
| LangSmith: add env vars, verify traces appear in dashboard | 0.5h |
| FastAPI: `POST /api/chat` endpoint connected to agent | 2h |
| Integration test: `curl` a real company (AAPL, MSFT, NVDA) — verify output quality | 1h |
| Prompt refinement: iterate on synthesizer system prompt based on test output | 1h |

**GitHub milestone:** `v0.2-agent` — `curl` a company name, receive a full Markdown analysis.

---

## Week 3 — Frontend (15h)

**Goal:** Next.js chat UI running in browser, connected to FastAPI, rendering Markdown.

| Task | Hours |
|------|-------|
| Next.js 14 project setup: App Router, TypeScript, Tailwind CSS | 1h |
| `types/chat.ts`: `Message`, `ChatRequest`, `ChatResponse` types | 0.5h |
| `lib/api.ts`: `fetch` wrapper for `POST /api/chat` | 1h |
| `ChatContainer` component: manages `messages` state | 1.5h |
| `MessageList` component: scrollable list, auto-scrolls to bottom | 1.5h |
| `MessageBubble` component: user vs. agent styles + `react-markdown` rendering | 3h |
| `InputBar` component: text input + send button + Enter key handling | 1.5h |
| Loading state: spinner shown while agent is running | 1h |
| CORS config in FastAPI: allow `localhost:3000` and Vercel domain | 0.5h |
| Error handling: show friendly message if API call fails | 1h |
| Manual E2E test in browser: full flow end-to-end | 1.5h |
| Verify Markdown tables, bold text, headers render correctly | 1h |

**GitHub milestone:** `v0.3-frontend` — full demo-able in browser, locally.

---

## Week 4 — QA & Polish (15h)

**Goal:** Handle edge cases robustly. Improve analysis quality. Code ready for deployment.

| Task | Hours |
|------|-------|
| Edge case: invalid ticker (e.g., "XYZNOTREAL") — yfinance error → graceful agent response | 1.5h |
| Edge case: yfinance returns partial data — agent analyzes available data, flags missing | 1.5h |
| Edge case: user asks non-finance question — `router` routes to `responder`, polite redirect | 1h |
| Edge case: MCP tool timeout — retry logic in MCP Server | 1h |
| Prompt engineering: test 10 real companies, document weak spots, iterate | 3h |
| Mobile-responsive UI via Tailwind responsive classes | 1.5h |
| Improve Markdown rendering: custom components for tables and code blocks | 1.5h |
| Frontend error banner: distinct from normal messages, dismissible | 1h |
| Backend: structured logging (which ticker was requested, latency per node) | 1h |
| Code cleanup: remove TODOs, dead code, inline `print` statements | 1h |

**GitHub milestone:** `v0.4-polished` — ready for deployment.

---

## Week 5 — Deployment (15h)

**Goal:** Live on public URLs. Both services stable. Demo link in README.

| Task | Hours |
|------|-------|
| `Dockerfile` for backend: FastAPI + MCP Server in one container | 2h |
| Render.com: create account, new Web Service, connect GitHub repo | 0.5h |
| Render: set env vars (`GEMINI_API_KEY`, `LANGCHAIN_*`, `PORT`) | 0.5h |
| Render: first deployment attempt — debug until `/health` returns 200 | 2h |
| Vercel: create account, new project, connect frontend repo | 0.5h |
| Vercel: set `NEXT_PUBLIC_API_URL` to Render URL | 0.5h |
| FastAPI: update `ALLOWED_ORIGINS` to include Vercel production domain | 0.5h |
| E2E test on production: test 5 companies, all features | 2h |
| Cold-start UX: show "Warming up..." if first request takes >10s | 1.5h |
| Monitor LangSmith traces from production — verify they appear correctly | 1h |
| README: add live demo link, screenshot, and "Getting Started" instructions | 2h |
| Fix any production-specific bugs | 1.5h |

**GitHub milestone:** `v1.0-deployed` — public URL live, demo link in README.

---

## Week 6 — Portfolio Polish (15h)

**Goal:** Repo looks like a real engineering project. Explainable in an interview.

| Task | Hours |
|------|-------|
| Architecture diagram in Excalidraw or Mermaid (embed in README) | 2h |
| `docs/decisions.md`: 5 Architecture Decision Records (ADR format) | 3h |
| README rewrite: demo GIF/screenshot, tech stack badges, architecture section, setup guide | 2.5h |
| Demo recording: screen capture of full flow (company → analysis) | 1.5h |
| Post-MVP roadmap section in README: shows strategic thinking | 1h |
| LangSmith: screenshot 2-3 interesting traces for portfolio / LinkedIn | 1h |
| LinkedIn post draft: explain engineering decisions, not just "I built X" | 1.5h |
| Stretch: publish blog post on dev.to or Hashnode | 2h |
| Final bug sweep on live demo | 0.5h |

**GitHub milestone:** `v1.0-portfolio` — final portfolio state.

---

## What Goes to GitHub at Each Stage

| Week | Key commits | Why it matters |
|------|-------------|----------------|
| 1 | MCP Server + LangGraph skeleton | Shows incremental approach from day 1 |
| 2 | Full agent + FastAPI endpoint | Core engineering value visible |
| 3 | Next.js frontend | Full-stack reach visible |
| 4 | Tests + edge cases + prompt iterations | Shows engineering discipline |
| 5 | Dockerfile + Render config + live link | Shows ops and deployment thinking |
| 6 | ADRs + README + demo | Shows communication and documentation skills |

**Commit frequently within each week.** Recruiters and interviewers look at commit history — a flat history of one commit per week signals a homework assignment, not a professional project.

---

## Suggested Branch Strategy

```
main             ← always deployable
└── feature/week-1-foundation
└── feature/week-2-agent
└── feature/week-3-frontend
└── feature/week-4-polish
└── feature/week-5-deployment
└── feature/week-6-portfolio
```

Merge each branch to `main` at the end of the week via PR. This creates a clean commit history and makes the development progression visible.
