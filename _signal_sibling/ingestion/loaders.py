import os
import psycopg2
import psycopg2.extras
from pgvector.psycopg2 import register_vector
from config import COMPANIES


def get_connection():
    """Get PostgreSQL connection."""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", 5433)),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    register_vector(conn)
    return conn


def create_tables():
    """Create all required tables if they do not exist."""
    conn = get_connection()
    cur  = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            ticker      VARCHAR(10) PRIMARY KEY,
            name        TEXT NOT NULL,
            sector      VARCHAR(50),
            exchange    VARCHAR(10),
            cik         VARCHAR(20),
            logo_url    TEXT,
            created_at  TIMESTAMP DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS financials_raw (
            id          SERIAL PRIMARY KEY,
            ticker      VARCHAR(10) NOT NULL,
            metric_name VARCHAR(50) NOT NULL,
            period_end  DATE NOT NULL,
            form        VARCHAR(10),
            value       NUMERIC,
            created_at  TIMESTAMP DEFAULT NOW(),
            UNIQUE(ticker, metric_name, period_end, form)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS price_daily (
            id          SERIAL PRIMARY KEY,
            ticker      VARCHAR(10) NOT NULL,
            date        DATE NOT NULL,
            open        NUMERIC,
            high        NUMERIC,
            low         NUMERIC,
            close       NUMERIC NOT NULL,
            volume      BIGINT,
            vwap        NUMERIC,
            transactions INTEGER,
            created_at  TIMESTAMP DEFAULT NOW(),
            UNIQUE(ticker, date)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS earnings (
            id                  SERIAL PRIMARY KEY,
            ticker              VARCHAR(10) NOT NULL,
            period_end          DATE NOT NULL,
            eps_actual          NUMERIC,
            eps_estimate        NUMERIC,
            eps_surprise_pct    NUMERIC,
            revenue_actual      NUMERIC,
            revenue_estimate    NUMERIC,
            announcement_date   DATE,
            reporting_period    VARCHAR(20),
            created_at          TIMESTAMP DEFAULT NOW(),
            UNIQUE(ticker, period_end)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS filings_metadata (
            id              SERIAL PRIMARY KEY,
            ticker          VARCHAR(10) NOT NULL,
            filing_type     VARCHAR(10) NOT NULL,
            filing_date     DATE NOT NULL,
            fiscal_year     INTEGER,
            fiscal_quarter  VARCHAR(6),
            document_url    TEXT,
            embedded        BOOLEAN DEFAULT FALSE,
            created_at      TIMESTAMP DEFAULT NOW(),
            UNIQUE(ticker, filing_type, filing_date)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS embeddings (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            ticker          VARCHAR(10) NOT NULL,
            filing_type     VARCHAR(10) NOT NULL,
            filing_date     DATE NOT NULL,
            fiscal_year     INTEGER,
            fiscal_quarter  VARCHAR(6),
            section_label   VARCHAR(100),
            chunk_index     INTEGER NOT NULL,
            chunk_text      TEXT NOT NULL,
            embedding       vector(1024),
            token_count     INTEGER,
            created_at      TIMESTAMP DEFAULT NOW(),
            UNIQUE(ticker, filing_type, filing_date, section_label, chunk_index)
        );

        CREATE INDEX IF NOT EXISTS embeddings_hnsw_idx
            ON embeddings USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);

        CREATE INDEX IF NOT EXISTS embeddings_ticker_idx
            ON embeddings (ticker);

        CREATE INDEX IF NOT EXISTS embeddings_filing_date_idx
            ON embeddings (filing_date DESC);
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS failed_ingestions (
            id              SERIAL PRIMARY KEY,
            ticker          VARCHAR(10),
            metric_name     VARCHAR(50),
            filing_type     VARCHAR(10),
            error_type      VARCHAR(50),
            error_message   TEXT,
            attempted_at    TIMESTAMP DEFAULT NOW()
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            question        TEXT,
            answer          TEXT,
            ticker_context  VARCHAR(10),
            model_used      VARCHAR(50),
            tokens_in       INTEGER,
            tokens_out      INTEGER,
            latency_ms      INTEGER,
            classification  VARCHAR(30),
            retrieved_chunks INTEGER,
            session_id      VARCHAR(64),
            created_at      TIMESTAMP DEFAULT NOW()
        );
    """)

    conn.commit()
    cur.close()
    conn.close()


def upsert_companies():
    """Load all 70 companies into the companies table."""
    conn = get_connection()
    cur  = conn.cursor()
    for company in COMPANIES:
        cur.execute("""
            INSERT INTO companies (ticker, name, sector, exchange, cik)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (ticker) DO UPDATE SET
                name     = EXCLUDED.name,
                sector   = EXCLUDED.sector,
                exchange = EXCLUDED.exchange,
                cik      = EXCLUDED.cik;
        """, (company["ticker"], company["name"],
              company["sector"], company["exchange"], company["cik"]))
    conn.commit()
    cur.close()
    conn.close()


def upsert_financials(records: list):
    """Upsert financial metric records."""
    conn = get_connection()
    cur  = conn.cursor()
    psycopg2.extras.execute_values(cur, """
        INSERT INTO financials_raw (ticker, metric_name, period_end, form, value)
        VALUES %s
        ON CONFLICT (ticker, metric_name, period_end, form)
        DO UPDATE SET value = EXCLUDED.value;
    """, [(r["ticker"], r["metric_name"], r["period_end"],
           r["form"], r["value"]) for r in records])
    conn.commit()
    cur.close()
    conn.close()


def upsert_prices(records: list):
    """
    Upsert daily price records.

    Contract (Rule-3 amendment 2026-05-13):
      Each record dict MUST contain at minimum:
        - ticker (str)
        - date   (Python date object OR ISO yyyy-mm-dd string)
        - c      (close price, numeric, NOT NULL in DB)
      Optional fields (default to NULL if absent):
        - o, h, l, v, vw, n  (open, high, low, volume, vwap, transactions)
      The function MUST NEVER reference a "t" key. Raw Polygon bars from
      polygon_client.get_daily_ohlcv() use t (epoch-ms timestamp) instead
      of date; the Airflow DAG layer is responsible for normalizing
      t -> date before invoking this loader.
    """
    conn = get_connection()
    cur  = conn.cursor()
    psycopg2.extras.execute_values(cur, """
        INSERT INTO price_daily
            (ticker, date, open, high, low, close, volume, vwap, transactions)
        VALUES %s
        ON CONFLICT (ticker, date) DO NOTHING;
    """, [(r["ticker"], r["date"], r.get("o"), r.get("h"), r.get("l"),
           r["c"], r.get("v"), r.get("vw"), r.get("n")) for r in records])
    conn.commit()
    cur.close()
    conn.close()


def upsert_embeddings(chunks: list):
    """Upsert embedding chunks into pgvector table."""
    conn = get_connection()
    cur  = conn.cursor()
    for chunk in chunks:
        cur.execute("""
            INSERT INTO embeddings
                (ticker, filing_type, filing_date, fiscal_year,
                 fiscal_quarter, section_label, chunk_index,
                 chunk_text, embedding, token_count)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (ticker, filing_type, filing_date,
                         section_label, chunk_index)
            DO UPDATE SET
                chunk_text  = EXCLUDED.chunk_text,
                embedding   = EXCLUDED.embedding,
                token_count = EXCLUDED.token_count;
        """, (
            chunk["ticker"], chunk["filing_type"], chunk["filing_date"],
            chunk.get("fiscal_year"), chunk.get("fiscal_quarter"),
            chunk.get("section_label"), chunk["chunk_index"],
            chunk["chunk_text"], chunk["embedding"], chunk.get("token_count"),
        ))
    conn.commit()
    cur.close()
    conn.close()
