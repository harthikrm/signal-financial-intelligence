import os
import time
import requests
from config import POLYGON_RATE_LIMIT_SLEEP

POLYGON_BASE = "https://api.polygon.io"

_keys = [
    os.getenv("POLYGON_API_KEY_1"),
    os.getenv("POLYGON_API_KEY_2"),
]
_key_index = 0


def _get_key() -> str:
    return _keys[_key_index % len(_keys)]


def _rotate_key():
    global _key_index
    _key_index += 1


def _get(endpoint: str, params: dict = None) -> dict:
    """
    Make a GET request to Polygon API with dual-key failover.
    Rotates to second key if first fails.
    """
    if params is None:
        params = {}
    for attempt in range(len(_keys)):
        params["apiKey"] = _get_key()
        time.sleep(POLYGON_RATE_LIMIT_SLEEP)
        try:
            response = requests.get(
                f"{POLYGON_BASE}{endpoint}",
                params=params,
                timeout=30
            )
            if response.status_code == 429:
                _rotate_key()
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException:
            _rotate_key()
    raise Exception(f"Both Polygon API keys failed for {endpoint}")


def get_daily_ohlcv(ticker: str, date_from: str,
                    date_to: str) -> list:
    """
    Fetch daily OHLCV for a ticker over a date range.
    Returns list of daily bars.
    """
    data = _get(
        f"/v2/aggs/ticker/{ticker}/range/1/day/{date_from}/{date_to}",
        params={"adjusted": "true", "sort": "asc", "limit": 50000}
    )
    return data.get("results", [])


def get_earnings(ticker: str) -> list:
    """
    Fetch earnings history for a ticker.
    Returns EPS actual, estimate, revenue actual, estimate, surprise%.
    """
    data = _get(
        f"/vX/reference/financials",
        params={"ticker": ticker, "limit": 20,
                "timeframe": "quarterly", "sort": "period_of_report_date"}
    )
    return data.get("results", [])


def get_snapshot(tickers: list) -> list:
    """
    Fetch latest price snapshot for multiple tickers.
    Used for status bar refresh every 5 minutes.
    """
    ticker_str = ",".join(tickers)
    data = _get(
        f"/v2/snapshot/locale/us/markets/stocks/tickers",
        params={"tickers": ticker_str}
    )
    return data.get("tickers", [])
