from typing import Any

from fastapi import APIRouter, HTTPException

from models.database import db_cursor
from models.schemas import CompanyRow, IndicatorRow, MetricsRow, PriceSummaryRow

router = APIRouter(prefix="/company", tags=["company"], redirect_slashes=False)


def _unknown_ticker_message(ticker: str) -> str:
    return (
        f"{ticker} is not in Signal's coverage universe. "
        "Use a ticker from Signal's list of 70 monitored companies."
    )


def _valid_tickers() -> set[str]:
    with db_cursor() as cur:
        cur.execute("SELECT ticker FROM companies")
        rows = cur.fetchall()
    return {r[0].upper() for r in rows}


@router.get("/{ticker}")
def get_company(ticker: str) -> dict[str, Any]:
    t = ticker.upper()
    with db_cursor() as cur:
        cur.execute(
            "SELECT ticker, name, sector, exchange, cik FROM companies WHERE ticker = %s",
            (t,),
        )
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=_unknown_ticker_message(t))
    return CompanyRow(
        ticker=row[0], name=row[1], sector=row[2], exchange=row[3], cik=row[4]
    ).model_dump()


def _metrics_dict(row: tuple, colnames: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in zip(colnames, row):
        if isinstance(v, (bytes, memoryview)):
            out[k] = None
        elif hasattr(v, "__float__") and not isinstance(v, bool):
            out[k] = float(v)
        else:
            out[k] = v
    return out


def _latest_eps_from_earnings(cur: Any, ticker: str) -> float | None:
    """Most recent quarterly EPS from Polygon earnings ingest."""
    cur.execute(
        """
        SELECT eps_actual
        FROM earnings
        WHERE ticker = %s
          AND eps_actual IS NOT NULL
        ORDER BY period_end DESC NULLS LAST
        LIMIT 1
        """,
        (ticker,),
    )
    row = cur.fetchone()
    return _to_float(row[0]) if row else None


def _latest_non_null_metric(cur: Any, ticker: str, column: str) -> float | None:
    cur.execute(
        f"""
        SELECT "{column}" FROM fct_company_metrics
        WHERE ticker = %s AND "{column}" IS NOT NULL
        ORDER BY period_end DESC NULLS LAST
        LIMIT 1
        """,
        (ticker,),
    )
    row = cur.fetchone()
    return _to_float(row[0]) if row else None


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _enrich_metrics_with_price_data(
    cur: Any, ticker: str, data: dict[str, Any]
) -> dict[str, Any]:
    """Add market_cap, pe_ratio, and 52-week range from price_daily + fundamentals."""
    cur.execute(
        """
        SELECT close FROM price_daily
        WHERE ticker = %s
        ORDER BY date DESC NULLS LAST
        LIMIT 1
        """,
        (ticker,),
    )
    price_row = cur.fetchone()
    latest_price = _to_float(price_row[0]) if price_row else None

    cur.execute(
        """
        SELECT MAX(high) AS week_52_high, MIN(low) AS week_52_low
        FROM price_daily
        WHERE ticker = %s
          AND date >= CURRENT_DATE - INTERVAL '52 weeks'
        """,
        (ticker,),
    )
    range_row = cur.fetchone()
    if range_row:
        week_high = _to_float(range_row[0])
        week_low = _to_float(range_row[1])
        if week_high is not None:
            data["week_52_high"] = week_high
        if week_low is not None:
            data["week_52_low"] = week_low

    shares = _to_float(data.get("shares_outstanding"))
    if shares is None:
        shares = _latest_non_null_metric(cur, ticker, "shares_outstanding")
        if shares is not None:
            data["shares_outstanding"] = shares

    eps = _to_float(data.get("eps_diluted"))
    eps_from_earnings = False
    if eps is None:
        eps = _latest_non_null_metric(cur, ticker, "eps_diluted")
        if eps is not None:
            data["eps_diluted"] = eps

    if eps is None:
        eps = _latest_eps_from_earnings(cur, ticker)
        if eps is not None:
            eps_from_earnings = True
            data["eps_diluted"] = eps

    if latest_price is not None and shares is not None and shares > 0:
        data["market_cap"] = latest_price * shares

    if latest_price is not None and eps is not None and eps != 0:
        if eps_from_earnings:
            # Polygon earnings EPS is quarterly — annualize for P/E
            data["pe_ratio"] = latest_price / (eps * 4)
        else:
            data["pe_ratio"] = latest_price / eps

    return data


@router.get("/{ticker}/metrics")
def get_metrics(ticker: str) -> dict[str, Any]:
    t = ticker.upper()
    if t not in _valid_tickers():
        raise HTTPException(status_code=404, detail=_unknown_ticker_message(t))
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT column_name FROM information_schema.columns
            WHERE table_schema='public' AND table_name='fct_company_metrics'
            ORDER BY ordinal_position
            """
        )
        cols = [r[0] for r in cur.fetchall()]
        if not cols:
            return {"ticker": t, "data": {}}
        collist = ", ".join(f'"{c}"' for c in cols)
        cur.execute(
            f"""
            SELECT {collist} FROM fct_company_metrics
            WHERE ticker = %s
            ORDER BY period_end DESC NULLS LAST
            LIMIT 1
            """,
            (t,),
        )
        row = cur.fetchone()
        if not row:
            return {"ticker": t, "data": {}}
        data = _metrics_dict(row, cols)
        data = _enrich_metrics_with_price_data(cur, t, data)
    return MetricsRow(ticker=t, data=data).model_dump()


@router.get("/{ticker}/price/summary")
def price_summary(ticker: str) -> dict[str, Any]:
    t = ticker.upper()
    if t not in _valid_tickers():
        raise HTTPException(status_code=404, detail=_unknown_ticker_message(t))
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT close, date::text FROM price_daily
            WHERE ticker = %s
            ORDER BY date DESC NULLS LAST
            LIMIT 1
            """,
            (t,),
        )
        row = cur.fetchone()
    if not row:
        return PriceSummaryRow(ticker=t).model_dump()
    return PriceSummaryRow(ticker=t, last_close=float(row[0]), as_of=row[1]).model_dump()


@router.get("/{ticker}/indicators")
def indicators(ticker: str) -> dict[str, Any]:
    t = ticker.upper()
    if t not in _valid_tickers():
        raise HTTPException(status_code=404, detail=_unknown_ticker_message(t))
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT ticker, date::text, rsi_14, sma_50, sma_200
            FROM fct_price_indicators
            WHERE ticker = %s
            ORDER BY date DESC NULLS LAST
            LIMIT 1
            """,
            (t,),
        )
        row = cur.fetchone()
    if not row:
        return IndicatorRow(ticker=t).model_dump()
    return IndicatorRow(
        ticker=row[0],
        date=row[1],
        rsi_14=float(row[2]) if row[2] is not None else None,
        sma_50=float(row[3]) if row[3] is not None else None,
        sma_200=float(row[4]) if row[4] is not None else None,
    ).model_dump()


@router.get("/{ticker}/filings")
def filings(ticker: str) -> list[dict[str, Any]]:
    t = ticker.upper()
    if t not in _valid_tickers():
        raise HTTPException(status_code=404, detail=_unknown_ticker_message(t))
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT filing_type, filing_date::text, document_url, embedded
            FROM filings_metadata
            WHERE ticker = %s
            ORDER BY filing_date DESC NULLS LAST
            LIMIT 50
            """,
            (t,),
        )
        rows = cur.fetchall()
    return [
        {
            "filing_type": r[0],
            "filing_date": r[1],
            "document_url": r[2],
            "embedded": r[3],
        }
        for r in rows
    ]


@router.get("/{ticker}/metrics/historical")
def metrics_historical(ticker: str, limit: int = 12) -> list[dict[str, Any]]:
    t = ticker.upper()
    if t not in _valid_tickers():
        raise HTTPException(status_code=404, detail=_unknown_ticker_message(t))
    limit = max(1, min(40, limit))
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT period_end::text, revenue, net_income, net_margin, revenue_growth
            FROM int_company_metrics
            WHERE ticker = %s
            ORDER BY period_end DESC NULLS LAST
            LIMIT %s
            """,
            (t, limit),
        )
        rows = cur.fetchall()
    return [
        {
            "period_end": r[0],
            "revenue": float(r[1]) if r[1] is not None else None,
            "net_income": float(r[2]) if r[2] is not None else None,
            "net_margin": float(r[3]) if r[3] is not None else None,
            "revenue_growth": float(r[4]) if r[4] is not None else None,
        }
        for r in rows
    ]
