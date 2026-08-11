#!/usr/bin/env python3
"""
Phase 14 / manual Section 13.1 — XBRL (Signal DB) vs Yahoo Finance spot-check.

Tickers: NVDA, MSFT, JPM, TSLA, NFLX
Metrics: latest annual revenue and net_income from fct_company_metrics.
"""

from __future__ import annotations

import sys

import yfinance as yf

from _common import db_cursor, pass_fail, rel_diff_pct, setup_import_paths

FINANCIAL_TICKERS = ["NVDA", "MSFT", "JPM", "TSLA", "NFLX"]
METRICS = ("revenue", "net_income")


def _signal_latest_annual(ticker: str) -> dict[str, float | None]:
    try:
        with db_cursor() as cur:
            cur.execute(
                """
                SELECT revenue, net_income, period_end::text
                FROM fct_company_metrics
                WHERE ticker = %s
                  AND (period_type = 'annual' OR form ILIKE '10-K%%')
                ORDER BY period_end DESC NULLS LAST
                LIMIT 1
                """,
                (ticker,),
            )
            row = cur.fetchone()
    except Exception as exc:
        print(f"  DB error: {exc}")
        return {"revenue": None, "net_income": None, "period_end": None}
    if not row:
        return {"revenue": None, "net_income": None, "period_end": None}
    return {
        "revenue": float(row[0]) if row[0] is not None else None,
        "net_income": float(row[1]) if row[1] is not None else None,
        "period_end": row[2],
    }


def _yahoo_latest_annual(ticker: str, metric: str) -> float | None:
    t = yf.Ticker(ticker)
    try:
        stmt = t.income_stmt
    except Exception:
        stmt = None
    if stmt is None or stmt.empty:
        return None
    key = "Total Revenue" if metric == "revenue" else "Net Income"
    if key not in stmt.index:
        alt = "Net Income Common Stockholders" if metric == "net_income" else None
        if alt and alt in stmt.index:
            key = alt
        else:
            return None
    series = stmt.loc[key].dropna()
    if series.empty:
        return None
    return float(series.iloc[0])


def main() -> int:
    setup_import_paths()
    print("Signal financials vs Yahoo Finance (annual revenue & net income)")
    print("Tolerance: VERIFY_PCT_TOLERANCE env (default 2%)\n")
    failures = 0
    for ticker in FINANCIAL_TICKERS:
        print(f"=== {ticker} ===")
        sig = _signal_latest_annual(ticker)
        period = sig.get("period_end")
        for metric in METRICS:
            sig_val = sig.get(metric)
            yahoo = _yahoo_latest_annual(ticker, metric)
            diff = rel_diff_pct(sig_val, yahoo)
            line = pass_fail(diff, metric)
            print(
                f"  Signal ({period or 'n/a'}): {sig_val!r}  |  "
                f"Yahoo: {yahoo!r}  |  {line}"
            )
            if "FAIL" in line:
                failures += 1
            if "SKIP" in line and sig_val is None:
                print("  (no Signal row — run ingestion + dbt before expecting PASS)")
        print()
    if failures:
        print(f"RESULT: {failures} comparison(s) FAILED")
        return 1
    print("RESULT: all comparisons PASS or SKIP (no FAIL)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
