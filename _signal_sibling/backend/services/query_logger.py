import logging
from typing import Optional

from sqlalchemy import text

from models.database import get_engine

logger = logging.getLogger(__name__)


def log_query(
    question: str,
    answer: str,
    ticker_context: Optional[str],
    model_used: str,
    latency_ms: int,
    classification: str,
    retrieved_chunks: int,
    session_id: Optional[str],
    *,
    tokens_in: int = 0,
    tokens_out: int = 0,
) -> None:
    try:
        eng = get_engine()
        stmt = text(
            """
            INSERT INTO query_logs
                (question, answer, ticker_context, model_used,
                 tokens_in, tokens_out, latency_ms, classification,
                 retrieved_chunks, session_id)
            VALUES
                (:question, :answer, :ticker_context, :model_used,
                 :tokens_in, :tokens_out, :latency_ms, :classification,
                 :retrieved_chunks, :session_id)
            """
        )
        with eng.begin() as conn:
            conn.execute(
                stmt,
                {
                    "question": question[:8000],
                    "answer": answer[:16000],
                    "ticker_context": ticker_context,
                    "model_used": model_used[:50],
                    "tokens_in": tokens_in,
                    "tokens_out": tokens_out,
                    "latency_ms": latency_ms,
                    "classification": classification[:30],
                    "retrieved_chunks": retrieved_chunks,
                    "session_id": (session_id or "")[:64] or None,
                },
            )
    except Exception as e:
        logger.warning("query_logs insert failed (non-fatal): %s", e)
