from config import (XBRL_FALLBACK_CHAINS, XBRL_OVERRIDES,
                    FINANCIAL_COMPANIES, PERIOD_PREFERENCE)


def extract_metric(company_facts: dict, ticker: str,
                   metric_name: str) -> list:
    """
    Extract a financial metric from EDGAR companyfacts JSON.
    Uses fallback chain. Returns list of {period, value, form} dicts.
    Returns empty list if all fallbacks fail.
    """
    # Use override chain for financial companies
    if (ticker in FINANCIAL_COMPANIES and
            ticker in XBRL_OVERRIDES and
            metric_name in XBRL_OVERRIDES[ticker]):
        concepts = XBRL_OVERRIDES[ticker][metric_name]
    else:
        concepts = XBRL_FALLBACK_CHAINS.get(metric_name, [])

    us_gaap = company_facts.get("facts", {}).get("us-gaap", {})

    for concept in concepts:
        if concept not in us_gaap:
            continue
        units = us_gaap[concept].get("units", {})
        if "USD" in units:
            return _filter_periods(units["USD"], metric_name)
        if "shares" in units:
            return _filter_periods(units["shares"], metric_name)

    return []  # All fallbacks failed


def _filter_periods(facts: list, metric_name: str) -> list:
    """
    Filter facts to annual and quarterly periods.
    Prefer 10-K for annual, 10-Q for quarterly.
    Deduplicate by period.
    """
    seen = {}
    results = []

    for fact in facts:
        form = fact.get("form", "")
        end  = fact.get("end", "")
        val  = fact.get("val", None)

        if form not in ("10-K", "10-Q"):
            continue
        if val is None:
            continue

        # Deduplicate — prefer 10-K over 10-Q for same end date
        if end not in seen or (form == "10-K" and seen[end]["form"] == "10-Q"):
            seen[end] = {"period": end, "value": val, "form": form}

    return list(seen.values())
