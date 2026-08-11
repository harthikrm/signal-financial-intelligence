from __future__ import annotations

import re
from functools import lru_cache

from models.database import db_cursor


@lru_cache(maxsize=1)
def _ticker_aliases() -> dict[str, str]:
    """Map searchable alias (uppercase) -> canonical ticker."""
    aliases: dict[str, str] = {}
    try:
        with db_cursor() as cur:
            cur.execute("SELECT ticker, name FROM companies")
            rows = cur.fetchall()
    except Exception:
        return aliases

    for ticker, name in rows:
        t = str(ticker).upper()
        aliases[t] = t
        if name:
            name_upper = str(name).upper()
            aliases[name_upper] = t
            for word in re.findall(r"[A-Z0-9&.]+", name_upper):
                if len(word) >= 3:
                    aliases[word] = t
    return aliases


def tickers_in_question(question: str) -> set[str]:
    q = question.upper()
    aliases = _ticker_aliases()
    found: set[str] = set()

    for alias in sorted(aliases.keys(), key=len, reverse=True):
        if re.search(rf"\b{re.escape(alias)}\b", q):
            found.add(aliases[alias])

    return found


def tickers_from_tool_results(tool_results: list[dict]) -> set[str]:
    found: set[str] = set()
    for entry in tool_results:
        args = entry.get("args") or {}
        ticker = args.get("ticker")
        if ticker:
            found.add(str(ticker).upper())
        for t in args.get("tickers") or []:
            found.add(str(t).upper())

        result = entry.get("result")
        if isinstance(result, dict):
            for key in result:
                if str(key).upper() == key and 1 <= len(key) <= 6:
                    found.add(str(key).upper())
    return found


def allowed_tickers(question: str, tool_results: list[dict]) -> set[str]:
    """Tickers the user asked about or tools explicitly queried."""
    from_question = tickers_in_question(question)
    from_tools = tickers_from_tool_results(tool_results)
    if from_question:
        return from_question
    return from_tools


def filter_tool_results_by_tickers(
    tool_results: list[dict], allowed: set[str]
) -> list[dict]:
    if not allowed:
        return tool_results

    filtered: list[dict] = []
    for entry in tool_results:
        if entry.get("tool") != "search_filings":
            filtered.append(entry)
            continue

        result = entry.get("result")
        if not isinstance(result, list):
            filtered.append(entry)
            continue

        chunks = [
            chunk
            for chunk in result
            if isinstance(chunk, dict)
            and str(chunk.get("ticker", "")).upper() in allowed
        ]
        filtered.append({**entry, "result": chunks})
    return filtered
