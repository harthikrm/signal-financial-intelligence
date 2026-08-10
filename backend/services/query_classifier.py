import json
import logging
import os
import re
import time
from typing import Any

from openai import OpenAI

from models.database import db_cursor

logger = logging.getLogger(__name__)

_ALLOWED = frozenset(
    {"FILING", "GENERAL", "MULTI_COMPANY", "GUARDRAIL", "OUT_OF_SCOPE"}
)

# Refresh coverage from DB periodically (Cloud Run keeps process warm;
# a permanent cache went stale after companies were restored).
_COVERAGE_TTL_SEC = int(os.getenv("COVERAGE_TICKERS_TTL_SEC", "60"))
_coverage_cache: tuple[str, ...] = tuple()
_coverage_cached_at = 0.0


def _coverage_tickers_tuple() -> tuple[str, ...]:
    global _coverage_cache, _coverage_cached_at
    now = time.monotonic()
    if _coverage_cache and (now - _coverage_cached_at) < _COVERAGE_TTL_SEC:
        return _coverage_cache
    try:
        with db_cursor() as cur:
            cur.execute("SELECT ticker FROM companies ORDER BY ticker")
            _coverage_cache = tuple(r[0] for r in cur.fetchall())
            _coverage_cached_at = now
            return _coverage_cache
    except Exception as e:
        logger.warning("coverage tickers load failed: %s", e)
        return _coverage_cache


def _classifier_system_prompt() -> str:
    tickers = _coverage_tickers_tuple()
    ticker_block = ", ".join(tickers) if tickers else "(no rows in companies table)"
    return (
        "You are a query classifier for Signal, a financial intelligence "
        "platform covering 70 public companies. Classify the user "
        "question into exactly one category and extract any mentioned "
        "tickers from the coverage list provided.\n"
        "Return only valid JSON. No other text.\n"
        'Schema: {"category": "FILING", "tickers": ["NVDA"], "k": 5}\n\n'
        "Allowed category values (exactly one): "
        "FILING, GENERAL, MULTI_COMPANY, GUARDRAIL, OUT_OF_SCOPE.\n"
        "Coverage tickers (only these symbols may appear in tickers): "
        f"{ticker_block}\n\n"
        "Category definitions:\n"
        "- GENERAL: finance vocabulary, formulas, ratios, accounting concepts, "
        "macro/market mechanics, technical analysis concepts, screening "
        "frameworks, OR questions about a covered ticker that do NOT need "
        "SEC filing text (e.g. 'What is free cash flow?', 'Explain RSI', "
        "'technical analysis on SPOT', 'breakout patterns after a dip').\n"
        "- FILING: needs SEC filing excerpts or company-specific facts from "
        "10-K/10-Q/8-K for one or more covered tickers "
        "(e.g. NVIDIA risks in latest 10-K).\n"
        "- MULTI_COMPANY: compares or ties together 2+ covered tickers using "
        "filings or company-specific facts.\n"
        "- GUARDRAIL: explicit buy/sell/hold recommendations, price targets, "
        "legal/tax advice, or insider trading.\n"
        "- OUT_OF_SCOPE: NOT finance/markets, OR the question is ONLY about "
        "tickers/companies NOT in the coverage list, OR clearly unrelated "
        "(recipes, sports, personal life).\n"
        "Prefer GENERAL over OUT_OF_SCOPE for any markets/TA/finance education "
        "question. Prefer GENERAL over FILING when the user asks for TA, "
        "trends, or concepts and does not ask about filing contents.\n"
        "Map company names to coverage tickers when obvious "
        "(Spotify→SPOT, NVIDIA→NVDA).\n"
    )


def _k_for_category(category: str) -> int:
    if category == "FILING":
        return int(os.getenv("RAG_K_FILING", "5"))
    if category == "MULTI_COMPANY":
        return int(os.getenv("RAG_K_MULTI_COMPANY", "7"))
    return 0


def classify_query(question: str) -> dict[str, Any]:
    default: dict[str, Any] = {"category": "GENERAL", "tickers": [], "k": 0}
    try:
        cov_set = frozenset(_coverage_tickers_tuple())
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        model = os.getenv("LLM_MODEL_PRODUCTION", "gpt-4o-mini")
        max_tok = int(os.getenv("CLASSIFIER_MAX_TOKENS", "100"))
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _classifier_system_prompt()},
                {"role": "user", "content": question[:4000]},
            ],
            temperature=0,
            max_tokens=max_tok,
            response_format={"type": "json_object"},
        )
        raw = resp.choices[0].message.content or "{}"
        data = json.loads(raw)
        cat_raw = str(data.get("category", "GENERAL")).strip().upper()
        cat_raw = re.sub(r"\s+", "_", cat_raw)
        if cat_raw not in _ALLOWED:
            cat_raw = "GENERAL"
        raw_tickers = data.get("tickers") or []
        tickers: list[str] = []
        for t in raw_tickers:
            u = str(t).upper().strip()
            if u in cov_set:
                tickers.append(u)
        k = _k_for_category(cat_raw)
        return {"category": cat_raw, "tickers": tickers, "k": k}
    except Exception as e:
        logger.warning("classify_query failed, defaulting to GENERAL: %s", e)
        return default
