import json
import logging
import os
import re
from functools import lru_cache
from typing import Any

from openai import OpenAI

from models.database import db_cursor

logger = logging.getLogger(__name__)

_ALLOWED = frozenset(
    {"FILING", "GENERAL", "MULTI_COMPANY", "GUARDRAIL", "OUT_OF_SCOPE"}
)


@lru_cache(maxsize=1)
def _coverage_tickers_tuple() -> tuple[str, ...]:
    try:
        with db_cursor() as cur:
            cur.execute("SELECT ticker FROM companies ORDER BY ticker")
            return tuple(r[0] for r in cur.fetchall())
    except Exception as e:
        logger.warning("coverage tickers load failed: %s", e)
        return tuple()


def _classifier_system_prompt() -> str:
    tickers = _coverage_tickers_tuple()
    ticker_block = ", ".join(tickers) if tickers else "(no rows in companies table)"
    return (
        "You are a query classifier for Signal, a financial intelligence "
        "platform covering 70 S&P 500 companies. Classify the user "
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
        "macro or market mechanics WITHOUT needing SEC filing text for a specific "
        "covered company (e.g. 'What is free cash flow?', 'Explain beta', "
        "'How does a 10-K differ from a 10-Q?').\n"
        "- FILING: needs SEC filing excerpts or company-specific facts for one "
        "or more covered tickers (e.g. NVIDIA risks in latest 10-K).\n"
        "- MULTI_COMPANY: compares or ties together 2+ covered tickers using "
        "filings or company-specific facts.\n"
        "- GUARDRAIL: buy/sell/hold, price targets, legal/tax advice, insider "
        "trading, or other disallowed requests per typical brokerage research policy.\n"
        "- OUT_OF_SCOPE: NOT finance/markets, OR the question is ONLY about "
        "tickers/companies NOT in the coverage list, OR clearly unrelated "
        "(recipes, sports, personal life).\n"
        "When in doubt between GENERAL and FILING: if the user only wants a "
        "concept explanation and does not name a covered company needing filing "
        "facts, choose GENERAL.\n"
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
