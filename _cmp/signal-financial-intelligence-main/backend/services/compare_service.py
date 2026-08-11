import os
from typing import Any

from openai import OpenAI

COMPARE_PROMPT = """You are Signal's equity comparison engine.

Rules:
1. Use only factual, neutral language — no buy/sell language.
2. Prefer filing-based facts when comparing covered companies.
3. If data is missing, say so explicitly.
4. Structure the answer in exactly five sections with these headings:
   EXECUTIVE SUMMARY
   FINANCIAL COMPARISON
   VALUATION & MULTIPLES
   RISKS & CATALYSTS
   CROSS-SECTOR CONTEXT
5. When companies span sectors, call out sector differences in section 5.
6. Cite metrics with time period (FY, TTM, quarter).
7. End with one-sentence takeaway.

Tickers to compare: {tickers}
"""


def run_compare(tickers: list[str]) -> str:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    prompt = COMPARE_PROMPT.format(tickers=", ".join(tickers))
    model = os.getenv("LLM_MODEL_PRODUCTION", "gpt-4o-mini")
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt},
            {
                "role": "user",
                "content": "Produce the five-section comparison per the rules.",
            },
        ],
        temperature=0.2,
    )
    return (resp.choices[0].message.content or "").strip()


def run_compare_json(tickers: list[str]) -> dict[str, Any]:
    """Optional structured variant for /analysis if we extend schema later."""
    text = run_compare(tickers)
    return {"tickers": tickers, "analysis": text}
