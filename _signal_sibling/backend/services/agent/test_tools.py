import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from services.agent.tools import (
    compare_companies,
    get_company_metrics,
    get_earnings_history,
    get_price_history,
)

print("=== Testing get_company_metrics ===")
result = get_company_metrics.invoke({"ticker": "NVDA"})
print(f"Keys: {list(result.keys())}")
print(f"Revenue: {result.get('revenue')}")
print(f"Gross margin: {result.get('gross_margin')}")

print("\n=== Testing compare_companies ===")
result = compare_companies.invoke(
    {
        "tickers": ["NVDA", "AMD"],
        "metrics": ["revenue", "gross_margin", "revenue_growth"],
    }
)
print(result)

print("\n=== Testing get_earnings_history ===")
result = get_earnings_history.invoke({"ticker": "NVDA", "quarters": 4})
print(result)

print("\n=== Testing get_price_history ===")
result = get_price_history.invoke({"ticker": "NVDA", "days": 5})
print(f"Latest price: {result.get('latest_price')}")
print(f"52w high: {result.get('week_52_high')}")
