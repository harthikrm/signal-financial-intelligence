import logging
import os
import time
from typing import Any, Optional

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from guardrails.rules import check_guardrails
from models.database import db_cursor
from services import embedding_service, query_classifier, query_logger
from services.knowledge_prompt import KNOWLEDGE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_OUT_OF_SCOPE_REPLY = (
    "This question is outside Signal's filing research scope or coverage "
    "universe. I can answer from general finance knowledge only, not from "
    "retrieved SEC filings for Signal's covered companies."
)
_CLASSIFIER_GUARDRAIL_REPLY = (
    "This request cannot be completed within Signal's research and "
    "compliance guidelines."
)


def _ticker_context_value(tickers: list[str]) -> Optional[str]:
    if not tickers:
        return None
    first = tickers[0][:10]
    return first


def _retrieve_chunks(
    question: str, tickers: list[str], k: int
) -> list[dict[str, Any]]:
    if k <= 0:
        return []
    try:
        vec = embedding_service.embed_query(question)
    except Exception as e:
        logger.warning("embed_query failed: %s", e)
        return []
    vec_literal = "[" + ",".join(str(float(x)) for x in vec) + "]"
    rows: list[tuple[Any, ...]] = []
    try:
        with db_cursor() as cur:
            if tickers:
                cur.execute(
                    """
                    SELECT ticker, filing_type, filing_date::text,
                           section_label, chunk_text,
                           1 - (embedding <=> %s::vector) AS similarity
                    FROM embeddings
                    WHERE ticker = ANY(%s)
                      AND embedding IS NOT NULL
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (vec_literal, tickers, vec_literal, k),
                )
            else:
                cur.execute(
                    """
                    SELECT ticker, filing_type, filing_date::text,
                           section_label, chunk_text,
                           1 - (embedding <=> %s::vector) AS similarity
                    FROM embeddings
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (vec_literal, vec_literal, k),
                )
            rows = cur.fetchall()
    except Exception as e:
        logger.warning("embedding retrieval failed: %s", e)
        return []
    out: list[dict[str, Any]] = []
    for r in rows:
        out.append(
            {
                "ticker": r[0],
                "filing_type": r[1],
                "filing_date": r[2],
                "section_label": r[3] or "",
                "chunk_text": r[4] or "",
                "similarity": float(r[5]) if r[5] is not None else 0.0,
            }
        )
    return out


def _format_context(chunks: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for c in chunks:
        head = (
            f"[{c['ticker']} {c['filing_type']} {c['filing_date']} — "
            f"{c['section_label']}]"
        )
        parts.append(f"{head}\n{c['chunk_text']}")
    return "\n---\n".join(parts)


def _sources_from_chunks(chunks: list[dict[str, Any]]) -> list[str]:
    src: list[str] = []
    for c in chunks:
        lbl = c.get("section_label") or ""
        src.append(
            f"{c['ticker']} {c['filing_type']} {c['filing_date']}, {lbl}".strip()
        )
    return src


def _history_messages(history: list[dict[str, Any]]) -> list[Any]:
    msgs: list[Any] = []
    tail = history[-12:] if history else []
    for h in tail:
        role = str(h.get("role", "")).lower().strip()
        content = str(h.get("content", ""))
        if not content:
            continue
        if role == "user":
            msgs.append(HumanMessage(content=content))
        elif role == "assistant":
            msgs.append(AIMessage(content=content))
    return msgs


def answer_query(
    question: str,
    history: Optional[list[dict[str, Any]]] = None,
    session_id: Optional[str] = None,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    history = history or []

    refusal = check_guardrails(question)
    if refusal:
        latency_ms = int((time.perf_counter() - t0) * 1000)
        query_logger.log_query(
            question,
            refusal,
            None,
            "guardrail",
            latency_ms,
            "guardrail_regex",
            0,
            session_id,
        )
        return {"answer": refusal, "sources": [], "model_used": "guardrail"}

    cls = query_classifier.classify_query(question)
    category = cls["category"]
    tickers = list(cls.get("tickers") or [])
    k = int(cls.get("k") or 0)

    if category == "OUT_OF_SCOPE":
        latency_ms = int((time.perf_counter() - t0) * 1000)
        query_logger.log_query(
            question,
            _OUT_OF_SCOPE_REPLY,
            _ticker_context_value(tickers),
            "classifier",
            latency_ms,
            category,
            0,
            session_id,
        )
        return {
            "answer": _OUT_OF_SCOPE_REPLY,
            "sources": [],
            "model_used": "classifier",
        }

    if category == "GUARDRAIL":
        latency_ms = int((time.perf_counter() - t0) * 1000)
        query_logger.log_query(
            question,
            _CLASSIFIER_GUARDRAIL_REPLY,
            _ticker_context_value(tickers),
            "classifier",
            latency_ms,
            category,
            0,
            session_id,
        )
        return {
            "answer": _CLASSIFIER_GUARDRAIL_REPLY,
            "sources": [],
            "model_used": "classifier",
        }

    chunks = _retrieve_chunks(question, tickers, k)
    context = _format_context(chunks)
    sources = _sources_from_chunks(chunks)

    if context:
        user_content = (
            "Use these filing excerpts to answer. Cite inline.\n\n"
            f"FILING EXCERPTS:\n{context}\n\nQUESTION: {question}"
        )
    else:
        user_content = question

    model_name = os.getenv("LLM_MODEL_PRODUCTION", "gpt-4o-mini")
    max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1500"))
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.1"))

    messages: list[Any] = [
        SystemMessage(content=KNOWLEDGE_SYSTEM_PROMPT),
        *_history_messages(history),
        HumanMessage(content=user_content),
    ]

    tokens_in = 0
    tokens_out = 0
    answer_text = ""
    try:
        llm = ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        resp = llm.invoke(messages)
        answer_text = (resp.content or "").strip()
        usage = getattr(resp, "usage_metadata", None) or {}
        tokens_in = int(usage.get("input_tokens") or 0)
        tokens_out = int(usage.get("output_tokens") or 0)
    except Exception as e:
        logger.exception("LLM invoke failed: %s", e)
        answer_text = (
            "I could not complete this answer due to a temporary model error. "
            "Please try again shortly."
        )
        model_name = "error"

    latency_ms = int((time.perf_counter() - t0) * 1000)
    query_logger.log_query(
        question,
        answer_text,
        _ticker_context_value(tickers),
        model_name,
        latency_ms,
        category,
        len(chunks),
        session_id,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
    )
    return {
        "answer": answer_text,
        "sources": sources,
        "model_used": model_name,
    }
