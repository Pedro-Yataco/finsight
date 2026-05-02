from mcp.server.fastmcp import FastMCP
from app.mcp.tools.company import get_company_info as _get_company_info

mcp = FastMCP("finsight")


@mcp.tool()
def get_company_info(ticker: str) -> dict:
    """Get company info: name, sector, industry, description, employees, country, website."""
    return _get_company_info(ticker)


if __name__ == "__main__":
    mcp.run()
