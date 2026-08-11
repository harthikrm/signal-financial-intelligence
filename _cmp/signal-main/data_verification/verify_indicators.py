#!/usr/bin/env python3
"""
Phase 14 / manual Section 13.3 — RSI / MACD / SMA spot-check vs TradingView.

Compares Signal fct_price_indicators (RSI, SMA-50, SMA-200) and MACD recomputed
from price_daily via ingestion/indicator_engine.py for NVDA and AAPL.
Harthik compares printed values to TradingView manually.
"""

from __future__ import annotations

import sys

import pandas as pd

from _common import db_cursor, setup_import_paths

INDICATOR_TICKERS = ["NVDA", "AAPL"]
LOOKBACK_DAYS = 260


def _load_prices(ticker: str) -> pd.DataFrame:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT date, open, high, low, close, volume, vwap
            FROM price_daily
            WHERE ticker = %s
            ORDER BY date ASC
            """,
            (ticker,),
        )
        rows = cur.fetchall()
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(
        rows, columns=["date", "open", "high", "low", "close", "volume", "vwap"]
    )
    return df.tail(LOOKBACK_DAYS)


def _signal_mart(ticker: str) -> dict | None:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT date::text, rsi_14, sma_50, sma_200
            FROM fct_price_indicators
            WHERE ticker = %s
            ORDER BY date DESC NULLS LAST
            LIMIT 1
            """,
            (ticker,),
        )
        row = cur.fetchone()
    if not row:
        return None
    return {
        "date": row[0],
        "rsi_14": row[1],
        "sma_50": row[2],
        "sma_200": row[3],
    }


def main() -> int:
    setup_import_paths()
    from indicator_engine import compute_all_indicators

    print("Signal indicators — compare latest values to TradingView")
    print("(MACD is computed locally from price_daily; mart has RSI + SMAs)\n")
    for ticker in INDICATOR_TICKERS:
        print(f"=== {ticker} ===")
        mart = _signal_mart(ticker)
        if mart:
            print(
                f"  fct_price_indicators @ {mart['date']}: "
                f"RSI={mart['rsi_14']}, SMA50={mart['sma_50']}, SMA200={mart['sma_200']}"
            )
        else:
            print("  fct_price_indicators: no rows (run dbt after price load)")

        prices = _load_prices(ticker)
        if prices.empty:
            print("  price_daily: empty — SKIP MACD recompute")
            print()
            continue
        ind = compute_all_indicators(prices)
        last = ind.iloc[-1]
        print(
            f"  Recomputed @ {last['date'].date()}: "
            f"RSI={last.get('rsi_14'):.4f}, "
            f"SMA50={last.get('sma_50'):.4f}, "
            f"SMA200={last.get('sma_200'):.4f}, "
            f"MACD={last.get('macd_line'):.4f}, "
            f"Signal={last.get('macd_signal'):.4f}, "
            f"Hist={last.get('macd_histogram'):.4f}"
        )
        print("  → Open TradingView, same symbol/date, compare RSI/MACD/SMA\n")
    print("RESULT: review complete when values match TradingView within your tolerance")
    return 0


if __name__ == "__main__":
    sys.exit(main())
