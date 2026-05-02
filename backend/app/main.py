from dotenv import load_dotenv
load_dotenv()  # loads .env into os.environ before any LLM init

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_mcp_adapters.tools import load_mcp_tools
from app.config import settings
from app.mcp.client import create_mcp_client, MCP_SERVER_NAME
from app.agent.graph import create_graph
from app.routes import chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = create_mcp_client()
    async with client.session(MCP_SERVER_NAME) as session:
        tools = await load_mcp_tools(session)
        app.state.graph = create_graph(tools)
        yield  # session stays alive while app runs


app = FastAPI(title="FinSight API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
