from mcp.server.fastmcp import FastMCP
from app.mcp.tools.company import get_company_info as _get_company_info
from app.mcp.tools.financials import get_financials as _get_financials
from app.mcp.tools.metrics import get_key_metrics as _get_key_metrics
from app.mcp.tools.price import get_price_history as _get_price_history

mcp = FastMCP("finsight")


@mcp.tool()
def get_company_info(ticker: str) -> dict:
    """Get company identity: name, sector, industry, description, employees, country, website."""
    return _get_company_info(ticker)


@mcp.tool()
def get_financials(ticker: str) -> dict:
    """Get financial statements: revenue history, margins, EBITDA, FCF, total debt, cash."""
    return _get_financials(ticker)


@mcp.tool()
def get_key_metrics(ticker: str) -> dict:
    """Get valuation and profitability metrics: P/E, P/B, ROE, ROA, EV/EBITDA, beta."""
    return _get_key_metrics(ticker)


@mcp.tool()
def get_price_history(ticker: str) -> dict:
    """Get price data: current price, 52-week range, moving averages, 1Y and 3Y reference prices."""
    return _get_price_history(ticker)


if __name__ == "__main__":
    mcp.run()
