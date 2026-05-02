import yfinance as yf


def get_company_info(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker.upper())
        info = t.info
        if not info or "quoteType" not in info:
            return {"error": f"No data found for ticker '{ticker}'"}
        return {
            "name": info.get("longName") or info.get("shortName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "description": info.get("longBusinessSummary", ""),
            "country": info.get("country", ""),
            "employees": info.get("fullTimeEmployees"),
            "website": info.get("website", ""),
        }
    except Exception as e:
        return {"error": str(e)}
