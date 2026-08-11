import os
from typing import Any

from openai import OpenAI

from models.database import db_cursor

COMPARE_SYSTEM = """You are Signal's equity comparison engine.

Hard rules:
1. Use ONLY the PLATFORM METRICS block provided by the user. Do not invent or recall numbers from training data.
2. If a metric is null/missing/N/A, say so explicitly — never fabricate a substitute.
3. Use only factual, neutral language — no buy/sell recommendations.
4. Cite every figure with its period label from the data (e.g. period_end, period_type, TTM fields).
5. Structure the answer in exactly five sections with these headings:
   EXECUTIVE SUMMARY
   FINANCIAL COMPARISON
   VALUATION & MULTIPLES
   RISKS & CATALYSTS
   CROSS-SECTOR CONTEXT
6. When companies span sectors, call out sector differences in section 5.
7. End with one-sentence takeaway grounded in the provided metrics.
"""

_METRIC_KEYS = (
    "ticker",
    "period_end",
    "period_type",
    "fiscal_year",
    "form",
    "revenue",
    "revenue_ttm",
    "prior_revenue",
    "revenue_growth",
    "gross_profit",
    "gross_profit_ttm",
    "gross_margin",
    "gross_margin_ttm",
    "net_income",
    "net_income_ttm",
    "net_margin",
    "net_margin_ttm",
    "operating_income",
    "free_cash_flow",
    "fcf_ttm",
    "fcf_margin_ttm",
    "ebitda",
    "total_assets",
    "total_equity",
    "total_debt",
    "cash",
    "shares_outstanding",
    "eps_diluted",
    "market_cap",
    "pe_ratio",
    "roe",
    "roa",
)


def _fetch_latest_metrics(tickers: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with db_cursor() as cur:
        for t in tickers:
            cur.execute(
                """
                SELECT m.*, c.name, c.sector,
                       p.close AS last_close, p.date AS price_as_of
                FROM fct_company_metrics m
                LEFT JOIN companies c ON c.ticker = m.ticker
                LEFT JOIN LATERAL (
                    SELECT close, date
                    FROM price_daily
                    WHERE ticker = m.ticker
                    ORDER BY date DESC NULLS LAST
                    LIMIT 1
                ) p ON TRUE
                WHERE m.ticker = %s
                ORDER BY m.period_end DESC NULLS LAST
                LIMIT 1
                """,
                (t.upper(),),
            )
            row = cur.fetchone()
            if not row:
                out.append({"ticker": t.upper(), "error": "no metrics row"})
                continue
            colnames = [d[0] for d in cur.description]
            raw = dict(zip(colnames, row))
            shares = raw.get("shares_outstanding")
            close = raw.get("last_close")
            eps = raw.get("eps_diluted")
            market_cap = None
            pe_ratio = None
            try:
                if shares is not None and close is not None:
                    market_cap = float(shares) * float(close)
                if eps is not None and float(eps) != 0 and close is not None:
                    pe_ratio = float(close) / float(eps)
            except (TypeError, ValueError, ZeroDivisionError):
                pass

            slim: dict[str, Any] = {}
            for k in _METRIC_KEYS:
                if k == "market_cap":
                    slim[k] = market_cap
                elif k == "pe_ratio":
                    slim[k] = pe_ratio
                elif k in raw:
                    v = raw[k]
                    slim[k] = float(v) if hasattr(v, "as_tuple") else v
            slim["name"] = raw.get("name")
            slim["sector"] = raw.get("sector")
            slim["last_close"] = float(close) if close is not None else None
            slim["price_as_of"] = str(raw.get("price_as_of") or "")
            out.append(slim)
    return out


def _format_metrics_block(rows: list[dict[str, Any]]) -> str:
    lines: list[str] = ["PLATFORM METRICS (authoritative — use only these):"]
    for r in rows:
        lines.append("---")
        for k, v in r.items():
            lines.append(f"  {k}: {v}")
    return "\n".join(lines)


def run_compare(tickers: list[str]) -> str:
    metrics = _fetch_latest_metrics(tickers)
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    model = os.getenv("LLM_MODEL_PRODUCTION", "gpt-4o-mini")
    user = (
        f"Tickers: {', '.join(tickers)}\n\n"
        f"{_format_metrics_block(metrics)}\n\n"
        "Produce the five-section comparison using ONLY the platform metrics above."
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": COMPARE_SYSTEM},
            {"role": "user", "content": user},
        ],
        temperature=0.1,
    )
    return (resp.choices[0].message.content or "").strip()


def run_compare_json(tickers: list[str]) -> dict[str, Any]:
    text = run_compare(tickers)
    return {"tickers": tickers, "analysis": text}
