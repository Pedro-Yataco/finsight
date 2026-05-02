import yfinance as yf


def _safe_int(val) -> int | None:
    try:
        f = float(val)
        return None if f != f else int(f)  # NaN check: NaN != NaN
    except (TypeError, ValueError):
        return None


def get_financials(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker.upper())
        info = t.info
        if not info or "quoteType" not in info:
            return {"error": f"No data found for ticker '{ticker}'"}

        revenue_history: dict = {}
        gross_profit_history: dict = {}
        net_income_history: dict = {}

        try:
            stmt = t.income_stmt  # rows=line items, cols=annual dates (most recent first)
            if stmt is not None and not stmt.empty:
                for col in list(stmt.columns)[:4]:
                    year = str(col.year)
                    if "Total Revenue" in stmt.index:
                        revenue_history[year] = _safe_int(stmt.at["Total Revenue", col])
                    if "Gross Profit" in stmt.index:
                        gross_profit_history[year] = _safe_int(stmt.at["Gross Profit", col])
                    if "Net Income" in stmt.index:
                        net_income_history[year] = _safe_int(stmt.at["Net Income", col])
        except Exception:
            pass

        return {
            "revenue_history": revenue_history,
            "gross_profit_history": gross_profit_history,
            "net_income_history": net_income_history,
            "gross_margins": info.get("grossMargins"),
            "operating_margins": info.get("operatingMargins"),
            "profit_margins": info.get("profitMargins"),
            "total_revenue_ttm": info.get("totalRevenue"),
            "ebitda": info.get("ebitda"),
            "free_cashflow": info.get("freeCashflow"),
            "total_debt": info.get("totalDebt"),
            "cash_and_equivalents": info.get("totalCash"),
        }
    except Exception as e:
        return {"error": str(e)}
