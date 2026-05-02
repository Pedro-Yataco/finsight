import os
import sys
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient

_BACKEND_DIR = str(Path(__file__).resolve().parent.parent.parent)
MCP_SERVER_NAME = "finsight"


def create_mcp_client() -> MultiServerMCPClient:
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    if _BACKEND_DIR not in pythonpath:
        env["PYTHONPATH"] = _BACKEND_DIR + (os.pathsep + pythonpath if pythonpath else "")

    return MultiServerMCPClient(
        {
            MCP_SERVER_NAME: {
                "command": sys.executable,
                "args": ["-m", "app.mcp.server"],
                "transport": "stdio",
                "env": env,
            }
        }
    )
