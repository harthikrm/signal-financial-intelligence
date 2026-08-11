"""
Initial blocking load DAG.
Runs ONCE to load all historical data for all 70 companies.
May 2021 to May 2026. Sequential by sector.
Expected runtime: 2-4 hours.
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.insert(0, "/opt/airflow/ingestion")

from config import COMPANIES, DATE_FROM, DATE_TO, XBRL_FALLBACK_CHAINS
from edgar_client import get_company_facts, get_filing_list, get_filing_text
from polygon_client import get_daily_ohlcv, get_earnings
from xbrl_parser import extract_metric
from embedding_engine import chunk_filing, embed_chunks
from loaders import (create_tables, upsert_companies, upsert_financials,
                     upsert_prices, upsert_embeddings)
from failed_ingestions import log_failure
import pandas as pd

default_args = {
    "owner": "harthik",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def task_create_tables():
    create_tables()
    upsert_companies()


def task_ingest_financials():
    """Pull XBRL facts for all 70 companies."""
    for company in COMPANIES:
        ticker = company["ticker"]
        cik    = company["cik"]
        try:
            facts   = get_company_facts(cik)
            records = []
            for metric_name in XBRL_FALLBACK_CHAINS.keys():
                values = extract_metric(facts, ticker, metric_name)
                for v in values:
                    records.append({
                        "ticker":      ticker,
                        "metric_name": metric_name,
                        "period_end":  v["period"],
                        "form":        v["form"],
                        "value":       v["value"],
                    })
            if records:
                upsert_financials(records)
        except Exception as e:
            log_failure(ticker=ticker, error_type="XBRL",
                        error_message=str(e))


def task_ingest_prices():
    """Pull 5-year daily OHLCV for all 70 companies."""
    for company in COMPANIES:
        ticker = company["ticker"]
        try:
            bars = get_daily_ohlcv(ticker, DATE_FROM, DATE_TO)
            # Rule-3 amendment 2026-05-13 — normalize raw Polygon bars
            # (which use "t" = epoch-ms) into a Python date object before
            # calling upsert_prices, whose contract forbids a "t" key.
            # See loaders.upsert_prices docstring for the full record contract.
            records = []
            for bar in bars:
                record = {"ticker": ticker, **bar}
                if "t" in record:
                    record["date"] = pd.to_datetime(record["t"],
                                                    unit="ms").date()
                    del record["t"]
                records.append(record)
            if records:
                upsert_prices(records)
        except Exception as e:
            log_failure(ticker=ticker, error_type="PRICES",
                        error_message=str(e))


def task_ingest_earnings():
    """Pull earnings history for all 70 companies."""
    from loaders import get_connection
    import psycopg2.extras
    for company in COMPANIES:
        ticker = company["ticker"]
        try:
            earnings = get_earnings(ticker)
            if not earnings:
                continue
            conn = get_connection()
            cur  = conn.cursor()
            for e in earnings:
                cur.execute("""
                    INSERT INTO earnings
                        (ticker, period_end, eps_actual, eps_estimate,
                         eps_surprise_pct, revenue_actual, revenue_estimate,
                         announcement_date, reporting_period)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (ticker, period_end) DO NOTHING;
                """, (
                    ticker,
                    e.get("period_of_report_date"),
                    e.get("diluted_eps"),
                    None,
                    None,
                    e.get("revenues"),
                    None,
                    e.get("filing_date"),
                    e.get("timeframe"),
                ))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            log_failure(ticker=ticker, error_type="EARNINGS",
                        error_message=str(e))


def task_ingest_filings_and_embed():
    """Pull 10-K, 10-Q, 8-K filings and embed them."""
    for filing_type in ["10-K", "10-Q", "8-K"]:
        for company in COMPANIES:
            ticker = company["ticker"]
            cik    = company["cik"]
            try:
                filings = get_filing_list(cik, filing_type,
                                          DATE_FROM, DATE_TO)
                for filing in filings:
                    try:
                        text   = get_filing_text(filing["document_url"])
                        chunks = chunk_filing(
                            text, ticker, filing_type,
                            filing["filing_date"]
                        )
                        embedded = embed_chunks(chunks)
                        upsert_embeddings(embedded)
                    except Exception as e:
                        log_failure(ticker=ticker, filing_type=filing_type,
                                    error_type="EMBED", error_message=str(e))
            except Exception as e:
                log_failure(ticker=ticker, filing_type=filing_type,
                            error_type="FILING_LIST", error_message=str(e))


with DAG(
    dag_id="signal_initial_load",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["signal", "initial"],
) as dag:

    t1 = PythonOperator(task_id="create_tables",
                        python_callable=task_create_tables)
    t2 = PythonOperator(task_id="ingest_financials",
                        python_callable=task_ingest_financials)
    t3 = PythonOperator(task_id="ingest_prices",
                        python_callable=task_ingest_prices)
    t4 = PythonOperator(task_id="ingest_earnings",
                        python_callable=task_ingest_earnings)
    t5 = PythonOperator(task_id="ingest_filings_and_embed",
                        python_callable=task_ingest_filings_and_embed)

    t1 >> t2 >> t3 >> t4 >> t5
