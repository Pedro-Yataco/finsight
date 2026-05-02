import pytest
from app.mcp.tools.company import get_company_info
from app.mcp.tools.financials import get_financials
from app.mcp.tools.metrics import get_key_metrics
from app.mcp.tools.price import get_price_history


def test_company_info_returns_data():
    result = get_company_info("AAPL")
    assert "error" not in result
    assert result.get("name")
    assert result.get("sector")
    assert result.get("industry")


def test_financials_returns_revenue_history():
    result = get_financials("AAPL")
    assert "error" not in result
    assert "revenue_history" in result
    assert isinstance(result["revenue_history"], dict)
    assert len(result["revenue_history"]) >= 1


def test_financials_returns_margins():
    result = get_financials("AAPL")
    assert "error" not in result
    assert result.get("gross_margins") is not None


def test_key_metrics_returns_valuation():
    result = get_key_metrics("AAPL")
    assert "error" not in result
    assert result.get("market_cap") is not None
    assert result.get("pe_ratio") is not None or result.get("forward_pe") is not None


def test_price_history_returns_prices():
    result = get_price_history("AAPL")
    assert "error" not in result
    assert result.get("current_price") is not None
    assert result.get("52w_high") is not None
    assert result.get("52w_low") is not None


def test_price_history_returns_3y_reference():
    result = get_price_history("AAPL")
    assert "error" not in result
    assert result.get("price_3y_ago") is not None


def test_invalid_ticker_returns_error():
    for tool_fn in [get_company_info, get_financials, get_key_metrics, get_price_history]:
        result = tool_fn("XYZNOTREAL123")
        assert "error" in result, f"{tool_fn.__name__} should return error for invalid ticker"
