from datetime import datetime

from config import (XBRL_FALLBACK_CHAINS, XBRL_OVERRIDES,
                    FINANCIAL_COMPANIES, PERIOD_PREFERENCE)


def extract_metric(company_facts: dict, ticker: str,
                   metric_name: str) -> list:
    """
    Extract a financial metric from EDGAR companyfacts JSON.
    Uses fallback chain. Returns list of {period, value, form} dicts.
    Returns empty list if all fallbacks fail.

    Among matching concepts, prefer the one with the newest period_end
    (and more observations as a tie-break) so stale tags like AMD's
    legacy ``Revenues`` do not block modern contract-revenue tags.
    """
    # Use override chain for financial companies
    if (ticker in FINANCIAL_COMPANIES and
            ticker in XBRL_OVERRIDES and
            metric_name in XBRL_OVERRIDES[ticker]):
        concepts = XBRL_OVERRIDES[ticker][metric_name]
    else:
        concepts = XBRL_FALLBACK_CHAINS.get(metric_name, [])

    us_gaap = company_facts.get("facts", {}).get("us-gaap", {})

    candidates: list[tuple[str, int, list]] = []
    for concept in concepts:
        if concept not in us_gaap:
            continue
        units = us_gaap[concept].get("units", {})
        facts = None
        if "USD" in units:
            facts = units["USD"]
        elif "shares" in units:
            facts = units["shares"]
        if not facts:
            continue
        periods = _filter_periods(facts, metric_name)
        if not periods:
            continue
        latest = max(p["period"] for p in periods)
        candidates.append((latest, len(periods), periods))

    if not candidates:
        return []

    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    return candidates[0][2]


def _duration_days(fact: dict) -> int | None:
    start = fact.get("start")
    end = fact.get("end")
    if not start or not end:
        return None
    try:
        return (
            datetime.fromisoformat(end[:10]) - datetime.fromisoformat(start[:10])
        ).days
    except ValueError:
        return None


def _period_score(fact: dict) -> tuple:
    """
    Prefer single-period facts over YTD cumulatives.
    10-Q ≈ 90 days; 10-K ≈ 365 days. Form preference: 10-K over 10-Q for same end.
    """
    form = fact.get("form", "")
    days = _duration_days(fact)
    if days is None:
        duration_rank = 1  # point-in-time / unknown — keep but deprioritize vs perfect
    elif form == "10-Q" and 70 <= days <= 120:
        duration_rank = 3
    elif form == "10-K" and 330 <= days <= 400:
        duration_rank = 3
    elif form == "10-Q" and days > 120:
        duration_rank = 0  # likely YTD
    elif form == "10-K" and days < 300:
        duration_rank = 0
    else:
        duration_rank = 1
    form_rank = 2 if form == "10-K" else 1
    return (duration_rank, form_rank)


def _filter_periods(facts: list, metric_name: str) -> list:
    """
    Filter facts to annual and quarterly periods.
    Prefer duration-correct facts (avoid YTD) and 10-K over 10-Q for same end.
    Deduplicate by period end date.
    """
    best: dict[str, dict] = {}

    for fact in facts:
        form = fact.get("form", "")
        end = fact.get("end", "")
        val = fact.get("val", None)

        if form not in ("10-K", "10-Q"):
            continue
        if val is None or not end:
            continue

        score = _period_score(fact)
        # Drop clear YTD quarterly cumulatives when score says so
        if score[0] == 0:
            continue

        prev = best.get(end)
        candidate = {"period": end, "value": val, "form": form, "_score": score}
        if prev is None or score > prev["_score"]:
            best[end] = candidate

    # If everything was filtered (only YTD available), fall back to raw dedupe
    if not best:
        for fact in facts:
            form = fact.get("form", "")
            end = fact.get("end", "")
            val = fact.get("val", None)
            if form not in ("10-K", "10-Q") or val is None or not end:
                continue
            if end not in best or (form == "10-K" and best[end]["form"] == "10-Q"):
                best[end] = {"period": end, "value": val, "form": form, "_score": (0, 0)}

    return [
        {"period": v["period"], "value": v["value"], "form": v["form"]}
        for v in best.values()
    ]
