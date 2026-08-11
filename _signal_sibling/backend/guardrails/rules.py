import re
from typing import Optional

REFUSAL_BUY_SELL = (
    "Signal does not provide buy, sell, or hold recommendations. "
    "I can discuss fundamentals, risks, and filings instead."
)
REFUSAL_PRICE_PRED = (
    "Signal does not forecast stock prices. I can discuss historical "
    "performance, valuation context, and filing disclosures."
)
REFUSAL_LEGAL = (
    "I cannot provide legal or tax advice. Please consult a qualified professional."
)
REFUSAL_NON_FINANCE = (
    "I only answer finance and markets topics relevant to Signal's research scope."
)
REFUSAL_INSIDER = (
    "I cannot help with insider trading or strategies that violate securities laws."
)

_BUY_SELL = re.compile(
    r"\b(buy|sell|hold)\s+(this\s+)?stock\b|\bshould\s+i\s+(buy|sell)\b",
    re.I,
)
_PRICE_PRED = re.compile(
    r"\b(price\s+target|stock\s+price\s+will|where\s+will\s+.*\s+trade)\b", re.I
)
_LEGAL = re.compile(r"\b(legal advice|tax advice|cpa|attorney)\b", re.I)
_NON_FINANCE = re.compile(
    r"\b(recipe|sports score|movie|dating|python code|debug my)\b", re.I
)
_INSIDER = re.compile(r"\b(insider\s+trading|material\s+non\s*public)\b", re.I)


def guardrail_check(text: str) -> Optional[str]:
    """Return refusal string if blocked, else None."""
    if _BUY_SELL.search(text):
        return REFUSAL_BUY_SELL
    if _PRICE_PRED.search(text):
        return REFUSAL_PRICE_PRED
    if _LEGAL.search(text):
        return REFUSAL_LEGAL
    if _NON_FINANCE.search(text):
        return REFUSAL_NON_FINANCE
    if _INSIDER.search(text):
        return REFUSAL_INSIDER
    return None


_POLITICAL = re.compile(
    r"\b(vote for|elect\s+\w+|party platform|campaign)\b", re.I
)


def political_check(text: str) -> Optional[str]:
    if _POLITICAL.search(text):
        return (
            "I stay neutral on partisan politics. Ask about macro policy "
            "effects on markets or companies instead."
        )
    return None


def check_guardrails(text: str) -> Optional[str]:
    """Run all pattern checks; return refusal message or None."""
    return guardrail_check(text) or political_check(text)
