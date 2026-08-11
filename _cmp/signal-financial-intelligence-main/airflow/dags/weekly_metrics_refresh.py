"""
Weekly Metrics Refresh DAG.
Runs every Monday at 7am CT.
Refreshes XBRL financial metrics and price indicators for all 70 companies.
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import sys
sys.path.insert(0, "/opt/airflow/ingestion")

from config import COMPANIES, DATE_FROM, DATE_TO, XBRL_FALLBACK_CHAINS
from edgar_client import get_company_facts
from polygon_client import get_daily_ohlcv
from xbrl_parser import extract_metric
from loaders import upsert_financials, upsert_prices
from failed_ingestions import log_failure
import os
import pandas as pd

default_args = {
    "owner": "harthik",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
}


def refresh_financials():
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
                        "ticker": ticker, "metric_name": metric_name,
                        "period_end": v["period"], "form": v["form"],
                        "value": v["value"],
                    })
            if records:
                upsert_financials(records)
        except Exception as e:
            log_failure(ticker=ticker, error_type="WEEKLY_XBRL",
                        error_message=str(e))


def refresh_prices():
    from datetime import date
    from_date = (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
    to_date   = date.today().strftime("%Y-%m-%d")
    for company in COMPANIES:
        ticker = company["ticker"]
        try:
            bars = get_daily_ohlcv(ticker, from_date, to_date)
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
            log_failure(ticker=ticker, error_type="WEEKLY_PRICES",
                        error_message=str(e))


with DAG(
    dag_id="signal_weekly_metrics_refresh",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval="0 7 * * 1",
    catchup=False,
    tags=["signal", "weekly"],
) as dag:

    _dbt_target = os.getenv("DBT_TARGET", "prod")

    t1 = PythonOperator(task_id="refresh_financials",
                        python_callable=refresh_financials)
    t2 = PythonOperator(task_id="refresh_prices",
                        python_callable=refresh_prices)
    t3 = BashOperator(
        task_id="run_dbt",
        bash_command=(
            "cd /opt/airflow/dbt && "
            f"dbt run --profiles-dir . --target {_dbt_target} && "
            f"dbt test --profiles-dir . --target {_dbt_target}"
        ),
    )

    t1 >> t2 >> t3
