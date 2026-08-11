from loaders import get_connection


def log_failure(ticker: str, metric_name: str = None,
                filing_type: str = None, error_type: str = None,
                error_message: str = None):
    """Log a failed ingestion attempt. Pipeline continues after logging."""
    try:
        conn = get_connection()
        cur  = conn.cursor()
        cur.execute("""
            INSERT INTO failed_ingestions
                (ticker, metric_name, filing_type, error_type, error_message)
            VALUES (%s, %s, %s, %s, %s);
        """, (ticker, metric_name, filing_type, error_type,
              str(error_message)[:500]))
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass  # Never let logging crash the pipeline
