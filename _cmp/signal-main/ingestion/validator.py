"""
ingestion/validator.py — Data validation gate for the ingestion pipeline.

STATUS: Placeholder. Implementation deferred to Phase 7 and MUST be completed
        BEFORE the initial Airflow DAG run (i.e. before any production-grade
        ingest of EDGAR / Polygon data into signal_postgres).

Phase 7 will populate this module with per-record validators that act as the
final gate between raw API responses and writes to the database. Each validator
returns (is_valid: bool, error_message: str | None). Records that fail
validation are routed to `failed_ingestions.log_failure()` rather than silently
dropped, preserving every ingestion attempt for diagnostic review.

Planned validators (subject to refinement in Phase 7 task list):

    validate_financials_record(record: dict)   -> tuple[bool, str | None]
        - ticker exists in companies table
        - metric_name is in XBRL_FALLBACK_CHAINS keys (config.py)
        - period_end is a real date and not in the future
        - form is one of ("10-K", "10-Q", "8-K", "S-1", "DEF 14A")
        - value is numeric and within sanity bounds for that metric

    validate_price_record(record: dict)        -> tuple[bool, str | None]
        - ticker exists in companies table
        - date is a real trading day (not weekend; not pre-IPO)
        - close > 0; high >= low; volume >= 0
        - vwap is None or between low and high (when provided)

    validate_company_record(record: dict)      -> tuple[bool, str | None]
        - ticker is uppercase, 1-5 chars, no whitespace
        - sector is in the canonical sector list from config.SECTORS
        - exchange is one of ("NASDAQ", "NYSE", "AMEX")
        - cik is 10-digit zero-padded string

    validate_filing_metadata(record: dict)     -> tuple[bool, str | None]
        - ticker exists in companies table
        - filing_type is one of ("10-K", "10-Q", "8-K", "S-1", "DEF 14A")
        - filing_date is a real date and not in the future
        - fiscal_year is between 1990 and current_year + 1
        - document_url is a valid SEC EDGAR URL

CONTRACT (do not change without a Rule-3 amendment):
    Every public validator MUST be pure (no I/O, no DB calls, no API calls),
    so the entire Airflow DAG can dry-run validation against fixtures without
    a live database or network connection.
"""
