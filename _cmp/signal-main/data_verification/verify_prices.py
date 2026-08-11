#!/usr/bin/env python3
"""
Phase 14 — Polygon/Signal price_daily vs Yahoo Finance (last 5 trading days).

Spot-check tickers: NVDA, MSFT, JPM, TSLA, NFLX, AMD, AMZN, GOOGL, CRWD, V
"""

from __future__ import annotations

import sys
import pandas as pd
import yfinance as yf

from _common import db_cursor, pass_fail, rel_diff_pct, setup_import_paths

PRICE_TICKERS = [
    "NVDA",
    "MSFT",
    "JPM",
    "TSLA",
    "NFLX",
    "AMD",
    "AMZN",
    "GOOGL",
    "CRWD",
    "V",
]
TRADING_DAYS = 5


def _signal_closes(ticker: str) -> pd.DataFrame:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT date::text, close::float
            FROM price_daily
            WHERE ticker = %s
            ORDER BY date DESC
            LIMIT %s
            """,
            (ticker, TRADING_DAYS),
        )
        rows = cur.fetchall()
    if not rows:
        return pd.DataFrame(columns=["date", "close"])
    return pd.DataFrame(rows, columns=["date", "close"])


def _yahoo_closes(ticker: str) -> pd.DataFrame:
    hist = yf.Ticker(ticker).history(period="1mo", auto_adjust=False)
    if hist.empty:
        return pd.DataFrame(columns=["date", "close"])
    hist = hist.reset_index()
    hist["date"] = hist["Date"].dt.strftime("%Y-%m-%d")
    hist = hist.rename(columns={"Close": "close"})
    return hist[["date", "close"]].tail(TRADING_DAYS).iloc[::-1].reset_index(drop=True)


def main() -> int:
    setup_import_paths()
    print("Signal price_daily vs Yahoo Finance (last 5 sessions, close)")
    failures = 0
    for ticker in PRICE_TICKERS:
        print(f"\n=== {ticker} ===")
        sig = _signal_closes(ticker)
        yahoo = _yahoo_closes(ticker)
        if sig.empty:
            print("  SKIP — no rows in price_daily")
            continue
        yahoo_by_date = {r["date"]: r["close"] for _, r in yahoo.iterrows()}
        for _, row in sig.iterrows():
            d = row["date"]
            sig_c = float(row["close"])
            y_c = yahoo_by_date.get(d)
            if y_c is None:
                print(f"  {d}: Signal={sig_c:.4f}  Yahoo=missing  SKIP")
                continue
            diff = rel_diff_pct(sig_c, float(y_c))
            line = pass_fail(diff, d)
            print(f"  {d}: Signal={sig_c:.4f}  Yahoo={float(y_c):.4f}  {line}")
            if "FAIL" in line:
                failures += 1
    print()
    if failures:
        print(f"RESULT: {failures} day(s) FAILED")
        return 1
    print("RESULT: all comparisons PASS or SKIP (no FAIL)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
