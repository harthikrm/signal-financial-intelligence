from typing import Any

from fastapi import APIRouter, HTTPException

from models.database import db_cursor
from models.schemas import CompanyRow, IndicatorRow, MetricsRow, PriceSummaryRow

router = APIRouter(prefix="/company", tags=["company"])


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
    return {k: (v if not isinstance(v, (bytes, memoryview)) else None) for k, v in zip(colnames, row)}


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
