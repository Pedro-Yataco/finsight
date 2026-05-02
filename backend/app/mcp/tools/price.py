import yfinance as yf


def get_price_history(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker.upper())
        info = t.info
        if not info or "quoteType" not in info:
            return {"error": f"No data found for ticker '{ticker}'"}

        price_current = None
        price_3y_ago = None
        price_1y_ago = None

        try:
            hist = t.history(period="3y")
            if not hist.empty:
                price_current = round(float(hist["Close"].iloc[-1]), 2)
                price_3y_ago = round(float(hist["Close"].iloc[0]), 2)
                # ~252 trading days = 1 year
                if len(hist) >= 252:
                    price_1y_ago = round(float(hist["Close"].iloc[-252]), 2)
        except Exception:
            pass

        if price_current is None:
            price_current = info.get("currentPrice") or info.get("regularMarketPrice")

        return {
            "current_price": price_current,
            "price_3y_ago": price_3y_ago,
            "price_1y_ago": price_1y_ago,
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "50d_avg": info.get("fiftyDayAverage"),
            "200d_avg": info.get("twoHundredDayAverage"),
            "52w_change": info.get("52WeekChange"),
            "ytd_return": info.get("ytdReturn"),
            "shares_outstanding": info.get("sharesOutstanding"),
        }
    except Exception as e:
        return {"error": str(e)}
