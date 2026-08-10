#!/usr/bin/env python3
"""
Run Signal initial load without Airflow.
Phases: tables → financials → prices → earnings → filings/embeddings.

Usage (from repo root, with Cloud SQL Auth Proxy on localhost:5433):
  cd ingestion && python run_initial_load.py
  cd ingestion && python run_initial_load.py --skip-embeddings   # faster UI data
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import traceback

from dotenv import load_dotenv

# Repo root .env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
sys.path.insert(0, os.path.dirname(__file__))

from config import COMPANIES, DATE_FROM, DATE_TO, XBRL_FALLBACK_CHAINS  # noqa: E402
from edgar_client import get_company_facts, get_filing_list, get_filing_text  # noqa: E402
from polygon_client import get_daily_ohlcv, get_earnings  # noqa: E402
from xbrl_parser import extract_metric  # noqa: E402
from embedding_engine import chunk_filing, embed_chunks  # noqa: E402
from loaders import (  # noqa: E402
    create_tables,
    upsert_companies,
    upsert_financials,
    upsert_prices,
    upsert_embeddings,
)
from failed_ingestions import log_failure  # noqa: E402
import pandas as pd  # noqa: E402


def _banner(msg: str) -> None:
    print(f"\n{'=' * 60}\n{msg}\n{'=' * 60}", flush=True)


def phase_tables() -> None:
    _banner("1/5 create_tables + upsert_companies")
    create_tables()
    upsert_companies()
    print(f"OK — {len(COMPANIES)} companies", flush=True)


def phase_financials() -> None:
    _banner("2/5 ingest_financials (EDGAR XBRL)")
    ok = fail = 0
    for i, company in enumerate(COMPANIES, 1):
        ticker, cik = company["ticker"], company["cik"]
        print(f"[{i}/{len(COMPANIES)}] {ticker} financials...", flush=True)
        try:
            facts = get_company_facts(cik)
            records = []
            for metric_name in XBRL_FALLBACK_CHAINS.keys():
                for v in extract_metric(facts, ticker, metric_name):
                    records.append(
                        {
                            "ticker": ticker,
                            "metric_name": metric_name,
                            "period_end": v["period"],
                            "form": v["form"],
                            "value": v["value"],
                        }
                    )
            if records:
                upsert_financials(records)
            ok += 1
        except Exception as e:
            fail += 1
            log_failure(ticker=ticker, error_type="XBRL", error_message=str(e))
            print(f"  FAIL {ticker}: {e}", flush=True)
    print(f"Done financials — ok={ok} fail={fail}", flush=True)


def phase_prices() -> None:
    _banner("3/5 ingest_prices (Polygon)")
    ok = fail = 0
    for i, company in enumerate(COMPANIES, 1):
        ticker = company["ticker"]
        print(f"[{i}/{len(COMPANIES)}] {ticker} prices...", flush=True)
        try:
            bars = get_daily_ohlcv(ticker, DATE_FROM, DATE_TO)
            records = []
            for bar in bars:
                record = {"ticker": ticker, **bar}
                if "t" in record:
                    record["date"] = pd.to_datetime(record["t"], unit="ms").date()
                    del record["t"]
                records.append(record)
            if records:
                upsert_prices(records)
            ok += 1
        except Exception as e:
            fail += 1
            log_failure(ticker=ticker, error_type="PRICES", error_message=str(e))
            print(f"  FAIL {ticker}: {e}", flush=True)
    print(f"Done prices — ok={ok} fail={fail}", flush=True)


def _datapoint_value(section: dict | None, key: str):
    """Polygon financials store metrics as {value, unit, label, ...}."""
    if not section:
        return None
    node = section.get(key)
    if isinstance(node, dict):
        return node.get("value")
    return node


def _normalize_earnings_row(e: dict) -> dict | None:
    """
    Map Polygon /vX/reference/financials result → earnings table columns.
    API uses end_date + nested income_statement, not flat period_of_report_date.
    """
    period_end = e.get("end_date") or e.get("period_of_report_date")
    if not period_end:
        return None
    income = (e.get("financials") or {}).get("income_statement") or {}
    return {
        "period_end": period_end,
        "eps_actual": _datapoint_value(income, "diluted_earnings_per_share")
        or _datapoint_value(income, "basic_earnings_per_share"),
        "revenue_actual": _datapoint_value(income, "revenues"),
        "announcement_date": e.get("filing_date"),
        "reporting_period": e.get("fiscal_period") or e.get("timeframe"),
    }


def phase_earnings() -> None:
    _banner("4/5 ingest_earnings (Polygon)")
    from loaders import get_connection

    ok = fail = 0
    for i, company in enumerate(COMPANIES, 1):
        ticker = company["ticker"]
        print(f"[{i}/{len(COMPANIES)}] {ticker} earnings...", flush=True)
        try:
            earnings = get_earnings(ticker)
            if not earnings:
                ok += 1
                continue
            conn = get_connection()
            cur = conn.cursor()
            inserted = 0
            for e in earnings:
                row = _normalize_earnings_row(e)
                if not row:
                    continue
                cur.execute(
                    """
                    INSERT INTO earnings
                        (ticker, period_end, eps_actual, eps_estimate,
                         eps_surprise_pct, revenue_actual, revenue_estimate,
                         announcement_date, reporting_period)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (ticker, period_end) DO NOTHING;
                    """,
                    (
                        ticker,
                        row["period_end"],
                        row["eps_actual"],
                        None,
                        None,
                        row["revenue_actual"],
                        None,
                        row["announcement_date"],
                        row["reporting_period"],
                    ),
                )
                inserted += 1
            conn.commit()
            cur.close()
            conn.close()
            print(f"  inserted/seen rows={inserted}", flush=True)
            ok += 1
        except Exception as e:
            fail += 1
            log_failure(ticker=ticker, error_type="EARNINGS", error_message=str(e))
            print(f"  FAIL {ticker}: {e}", flush=True)
    print(f"Done earnings — ok={ok} fail={fail}", flush=True)


def phase_filings_embed() -> None:
    _banner("5/5 filings + embeddings (slow)")
    from loaders import get_connection

    # Prefetch already-embedded keys so resume skips without per-filing connects
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT ticker, filing_type, filing_date::text
        FROM filings_metadata
        WHERE embedded = TRUE
        """
    )
    already_embedded = {(r[0], r[1], r[2]) for r in cur.fetchall()}
    cur.close()
    conn.close()
    print(f"Resume cache: {len(already_embedded)} filings already embedded", flush=True)

    ok = fail = skipped = embedded_n = 0
    for filing_type in ["10-K", "10-Q", "8-K"]:
        for i, company in enumerate(COMPANIES, 1):
            ticker, cik = company["ticker"], company["cik"]
            try:
                filings = get_filing_list(cik, filing_type, DATE_FROM, DATE_TO)
            except Exception as e:
                fail += 1
                log_failure(
                    ticker=ticker,
                    filing_type=filing_type,
                    error_type="FILING_LIST",
                    error_message=str(e),
                )
                print(
                    f"[{filing_type}] [{i}/{len(COMPANIES)}] {ticker}... FAIL list: {e}",
                    flush=True,
                )
                continue

            todo = [
                f
                for f in filings
                if (ticker, filing_type, str(f["filing_date"])) not in already_embedded
            ]
            skip_here = len(filings) - len(todo)
            skipped += skip_here
            if not todo:
                print(
                    f"[{filing_type}] [{i}/{len(COMPANIES)}] {ticker}... "
                    f"skip all {skip_here}",
                    flush=True,
                )
                ok += 1
                continue

            print(
                f"[{filing_type}] [{i}/{len(COMPANIES)}] {ticker}... "
                f"embed {len(todo)} (skipped {skip_here})",
                flush=True,
            )
            for filing in todo:
                key = (ticker, filing_type, str(filing["filing_date"]))
                try:
                    text = get_filing_text(filing["document_url"])
                    chunks = chunk_filing(
                        text, ticker, filing_type, filing["filing_date"]
                    )
                    embedded = embed_chunks(chunks)
                    upsert_embeddings(embedded)

                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute(
                        """
                        INSERT INTO filings_metadata
                            (ticker, filing_type, filing_date, document_url, embedded)
                        VALUES (%s,%s,%s,%s,TRUE)
                        ON CONFLICT (ticker, filing_type, filing_date)
                        DO UPDATE SET embedded = TRUE;
                        """,
                        (
                            ticker,
                            filing_type,
                            filing["filing_date"],
                            filing.get("document_url"),
                        ),
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                    already_embedded.add(key)
                    embedded_n += 1
                except Exception as e:
                    fail += 1
                    log_failure(
                        ticker=ticker,
                        filing_type=filing_type,
                        error_type="EMBED",
                        error_message=str(e),
                    )
                    print(f"  FAIL embed {ticker} {filing.get('filing_date')}: {e}", flush=True)
            ok += 1
    print(
        f"Done filings/embed — passes≈{ok} newly_embedded={embedded_n} "
        f"skipped={skipped} fails={fail}",
        flush=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-embeddings",
        action="store_true",
        help="Skip filings/RAG embeddings (much faster; Explore still works)",
    )
    parser.add_argument(
        "--only",
        choices=["tables", "financials", "prices", "earnings", "embeddings"],
        help="Run a single phase",
    )
    args = parser.parse_args()

    required = ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        print(f"Missing env: {missing}", file=sys.stderr)
        return 1

    start = time.time()
    try:
        if args.only == "tables" or args.only is None:
            phase_tables()
        if args.only == "financials" or args.only is None:
            phase_financials()
        if args.only == "prices" or args.only is None:
            phase_prices()
        if args.only == "earnings" or args.only is None:
            phase_earnings()
        if args.only == "embeddings" or (
            args.only is None and not args.skip_embeddings
        ):
            phase_filings_embed()
        elif args.skip_embeddings:
            print("\nSkipping embeddings (--skip-embeddings)", flush=True)
    except Exception:
        traceback.print_exc()
        return 1

    mins = (time.time() - start) / 60
    print(f"\nInitial load finished in {mins:.1f} min", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
