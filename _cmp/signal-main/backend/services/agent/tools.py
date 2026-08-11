from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from langchain_core.tools import tool

from services.agent.db import get_db_connection
from services.embedding_service import embed_query


def _serialize_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (bytes, memoryview)):
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return float(value) if isinstance(value, float) else int(value)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if hasattr(value, "__float__"):
        try:
            return float(value)
        except (TypeError, ValueError):
            return str(value)
    return value


def _row_to_dict(row: tuple, colnames: list[str]) -> dict[str, Any]:
    return {k: _serialize_value(v) for k, v in zip(colnames, row)}


def _normalize_metric_name(name: str) -> str:
    key = (name or "").strip().lower().replace(" ", "_")
    aliases = {
        "r&d": "rd_expense",
        "rd": "rd_expense",
        "research_and_development": "rd_expense",
        "research_&_development": "rd_expense",
    }
    return aliases.get(key, name.strip())


def _vector_literal(vec: list[float]) -> str:
    return "[" + ",".join(str(float(x)) for x in vec) + "]"


@tool
def search_filings(
    query: str,
    ticker: str | None = None,
    filing_type: str | None = None,
    k: int = 5,
) -> list[dict]:
    """
    Search SEC filings using semantic similarity.
    Use this to find what companies said in their
    10-K, 10-Q, or 8-K filings about a specific topic.

    Args:
        query: Natural language search query
        ticker: Optional company ticker (e.g. NVDA)
        filing_type: Optional filter - 10-K, 10-Q, or 8-K
        k: Number of results to return (default 5)

    Returns list of dicts with:
        ticker, filing_type, filing_date,
        section_label, chunk_text, similarity
    """
    embedding = embed_query(query)
    vec_literal = _vector_literal(embedding)

    where_parts = ["embedding IS NOT NULL"]
    params: list[Any] = []

    if ticker:
        where_parts.append("ticker = %s")
        params.append(ticker.upper())
    if filing_type:
        where_parts.append("filing_type = %s")
        params.append(filing_type.upper())

    where_sql = " AND ".join(where_parts)

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            f"""
            SELECT ticker, filing_type, filing_date::text,
                   section_label, chunk_text,
                   1 - (embedding <=> %s::vector) AS similarity
            FROM embeddings
            WHERE {where_sql}
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            [vec_literal, *params, vec_literal, k],
        )
        rows = cur.fetchall()
    finally:
        cur.close()
        conn.close()

    return [
        {
            "ticker": r[0],
            "filing_type": r[1],
            "filing_date": str(r[2]) if r[2] is not None else None,
            "section_label": r[3],
            "chunk_text": (r[4] or "")[:500],
            "similarity": float(r[5]) if r[5] is not None else 0.0,
        }
        for r in rows
    ]


@tool
def get_company_metrics(ticker: str) -> dict:
    """
    Get latest financial metrics for a company from
    Signal's database. Use this for revenue, margins,
    growth rates, valuation, and balance sheet data.

    Args:
        ticker: Company ticker symbol (e.g. NVDA, MSFT)

    Returns dict with all available metrics including:
        revenue, gross_margin, operating_margin, net_margin,
        revenue_growth, market_cap, pe_ratio, week_52_high,
        week_52_low, revenue_ttm, free_cash_flow, ebitda
    """
    t = ticker.upper()
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT * FROM fct_company_metrics
            WHERE ticker = %s
            ORDER BY period_end DESC NULLS LAST
            LIMIT 1
            """,
            (t,),
        )
        row = cur.fetchone()
        if not row:
            return {"error": f"No data found for {ticker}"}

        columns = [desc[0] for desc in cur.description]
        metrics = _row_to_dict(row, columns)

        cur.execute(
            """
            SELECT close FROM price_daily
            WHERE ticker = %s
            ORDER BY date DESC NULLS LAST
            LIMIT 1
            """,
            (t,),
        )
        price_row = cur.fetchone()
        if price_row and metrics.get("shares_outstanding"):
            latest_price = _serialize_value(price_row[0])
            if latest_price is not None and metrics["shares_outstanding"]:
                metrics["latest_price"] = latest_price
                metrics["market_cap"] = latest_price * float(
                    metrics["shares_outstanding"]
                )

        cur.execute(
            """
            SELECT MAX(high) AS week_52_high, MIN(low) AS week_52_low
            FROM price_daily
            WHERE ticker = %s
              AND date >= CURRENT_DATE - INTERVAL '52 weeks'
            """,
            (t,),
        )
        range_row = cur.fetchone()
        if range_row:
            metrics["week_52_high"] = _serialize_value(range_row[0])
            metrics["week_52_low"] = _serialize_value(range_row[1])
    finally:
        cur.close()
        conn.close()

    return metrics


@tool
def compare_companies(tickers: list, metrics: list) -> dict:
    """
    Compare multiple companies side by side across
    specified financial metrics.

    Args:
        tickers: List of ticker symbols e.g. ["NVDA", "AMD", "INTC"]
        metrics: List of metric names e.g. ["revenue", "gross_margin"]
                 Available metrics: revenue, gross_margin,
                 operating_margin, net_margin, revenue_growth,
                 revenue_ttm, free_cash_flow, ebitda, roe, roa,
                 current_ratio, debt_to_equity, rd_expense

    Returns dict with each ticker as key and requested metrics as values
    """
    conn = get_db_connection()
    cur = conn.cursor()
    result: dict[str, Any] = {}

    try:
        for ticker in tickers:
            t = str(ticker).upper()
            cur.execute(
                """
                SELECT * FROM fct_company_metrics
                WHERE ticker = %s
                ORDER BY period_end DESC NULLS LAST
                LIMIT 1
                """,
                (t,),
            )
            row = cur.fetchone()
            if row:
                columns = [desc[0] for desc in cur.description]
                all_metrics = _row_to_dict(row, columns)
                result[t] = {
                    _normalize_metric_name(m): all_metrics.get(_normalize_metric_name(m))
                    for m in metrics
                    if _normalize_metric_name(m) in all_metrics
                }
            else:
                result[t] = {"error": "No data found"}
    finally:
        cur.close()
        conn.close()

    return result


@tool
def get_earnings_history(ticker: str, quarters: int = 8) -> list:
    """
    Get earnings history for a company including
    EPS actuals and revenue actuals by quarter.

    revenue_actual can be used as revenue fallback when
    fct_company_metrics has null revenue for a ticker.

    Args:
        ticker: Company ticker symbol
        quarters: Number of quarters to return (default 8)

    Returns list of dicts with:
        period_end, eps_actual, revenue_actual,
        reporting_period, announcement_date
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT period_end, eps_actual, revenue_actual,
                   reporting_period, announcement_date
            FROM earnings
            WHERE ticker = %s
              AND period_end IS NOT NULL
            ORDER BY period_end DESC NULLS LAST
            LIMIT %s
            """,
            (ticker.upper(), quarters),
        )
        rows = cur.fetchall()
    finally:
        cur.close()
        conn.close()

    return [
        {
            "period_end": str(r[0]) if r[0] is not None else None,
            "eps_actual": _serialize_value(r[1]),
            "revenue_actual": _serialize_value(r[2]),
            "reporting_period": r[3],
            "announcement_date": str(r[4]) if r[4] is not None else None,
        }
        for r in rows
    ]


@tool
def get_metrics_history(ticker: str, periods: int = 8) -> list[dict]:
    """
    Get historical financial metrics for a company across
    multiple periods from the metrics mart.
    Use this for trend analysis — gross margin over time,
    revenue progression, margin expansion/compression.

    Args:
        ticker: Company ticker symbol (e.g. TSLA, NVDA)
        periods: Number of periods to return (default 8)
                 Includes both quarterly and annual rows.

    Returns list of dicts ordered by period_end DESC with:
        period_end, period_type, revenue, gross_profit,
        gross_margin, operating_margin, net_margin,
        operating_income, net_income, revenue_growth,
        free_cash_flow, rd_expense
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT
                period_end, period_type, revenue, gross_profit,
                gross_margin, operating_margin, net_margin,
                operating_income, net_income, revenue_growth,
                free_cash_flow, rd_expense
            FROM fct_company_metrics
            WHERE ticker = %s
              AND period_type = 'quarterly'
            ORDER BY period_end DESC NULLS LAST
            LIMIT %s
            """,
            (ticker.upper(), periods),
        )
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
    finally:
        cur.close()
        conn.close()

    return [_row_to_dict(row, columns) for row in rows]


@tool
def get_price_history(ticker: str, days: int = 90) -> dict:
    """
    Get recent price history and market data for a company.

    Args:
        ticker: Company ticker symbol
        days: Number of trading days to return (default 90)

    Returns dict with:
        latest_price, day_change_pct, week_52_high,
        week_52_low, avg_volume, price_history (list)
    """
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT date, open, high, low, close, volume
            FROM price_daily
            WHERE ticker = %s
            ORDER BY date DESC NULLS LAST
            LIMIT %s
            """,
            (ticker.upper(), days),
        )
        rows = cur.fetchall()
    finally:
        cur.close()
        conn.close()

    if not rows:
        return {"error": f"No price data found for {ticker}"}

    prices = [
        {
            "date": str(r[0]) if r[0] is not None else None,
            "open": _serialize_value(r[1]),
            "high": _serialize_value(r[2]),
            "low": _serialize_value(r[3]),
            "close": _serialize_value(r[4]),
            "volume": int(r[5]) if r[5] is not None else None,
        }
        for r in rows
    ]

    latest = prices[0]
    prev = prices[1] if len(prices) > 1 else None

    highs = [p["high"] for p in prices if p["high"] is not None]
    lows = [p["low"] for p in prices if p["low"] is not None]
    volumes = [p["volume"] for p in prices if p["volume"] is not None]

    day_change_pct = None
    if (
        latest["close"] is not None
        and prev
        and prev["close"] is not None
        and prev["close"] != 0
    ):
        day_change_pct = round(
            (latest["close"] - prev["close"]) / prev["close"] * 100,
            2,
        )

    return {
        "latest_price": latest["close"],
        "previous_close": prev["close"] if prev else None,
        "day_change_pct": day_change_pct,
        "week_52_high": max(highs) if highs else None,
        "week_52_low": min(lows) if lows else None,
        "avg_volume": round(sum(volumes) / len(volumes)) if volumes else None,
        "price_history": prices[:30],
    }


TOOL_REGISTRY = {
    "search_filings": search_filings,
    "get_company_metrics": get_company_metrics,
    "compare_companies": compare_companies,
    "get_earnings_history": get_earnings_history,
    "get_metrics_history": get_metrics_history,
    "get_price_history": get_price_history,
}
