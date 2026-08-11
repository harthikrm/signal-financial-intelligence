"""
Daily 8-K Monitor DAG.
Runs every day at 6am CT.
Checks for new 8-K filings since last run.
Ingests, chunks, and embeds any new filings found.
"""
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.insert(0, "/opt/airflow/ingestion")

from config import COMPANIES
from edgar_client import get_filing_list, get_filing_text
from embedding_engine import chunk_filing, embed_chunks
from loaders import upsert_embeddings, get_connection
from failed_ingestions import log_failure

default_args = {
    "owner": "harthik",
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
}


def check_and_ingest_8k(**context):
    yesterday = (context["execution_date"] - timedelta(days=1)).strftime("%Y-%m-%d")
    today     = context["execution_date"].strftime("%Y-%m-%d")

    for company in COMPANIES:
        ticker = company["ticker"]
        cik    = company["cik"]
        try:
            filings = get_filing_list(cik, "8-K", yesterday, today)
            for filing in filings:
                # Check if already ingested
                conn = get_connection()
                cur  = conn.cursor()
                cur.execute("""
                    SELECT 1 FROM filings_metadata
                    WHERE ticker=%s AND filing_type='8-K'
                    AND filing_date=%s;
                """, (ticker, filing["filing_date"]))
                exists = cur.fetchone()
                cur.close()
                conn.close()

                if exists:
                    continue

                # New filing — ingest and embed
                text     = get_filing_text(filing["document_url"])
                chunks   = chunk_filing(text, ticker, "8-K",
                                        filing["filing_date"])
                embedded = embed_chunks(chunks)
                upsert_embeddings(embedded)

                # Mark as ingested
                conn = get_connection()
                cur  = conn.cursor()
                cur.execute("""
                    INSERT INTO filings_metadata
                        (ticker, filing_type, filing_date, embedded)
                    VALUES (%s, '8-K', %s, TRUE)
                    ON CONFLICT DO NOTHING;
                """, (ticker, filing["filing_date"]))
                conn.commit()
                cur.close()
                conn.close()

        except Exception as e:
            log_failure(ticker=ticker, filing_type="8-K",
                        error_type="DAILY_MONITOR", error_message=str(e))


with DAG(
    dag_id="signal_daily_8k_monitor",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval="0 6 * * *",
    catchup=False,
    tags=["signal", "daily"],
) as dag:

    PythonOperator(
        task_id="check_and_ingest_8k",
        python_callable=check_and_ingest_8k,
    )
