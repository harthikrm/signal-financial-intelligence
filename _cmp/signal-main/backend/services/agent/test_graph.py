"""Phase 2 sanity checks: search_filings tool + full LangGraph agent run."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

from services.agent.runner import run_agent
from services.agent.tools import search_filings

print("=== Testing search_filings ===")
filing_results = search_filings.invoke(
    {
        "query": "artificial intelligence data center demand",
        "ticker": "NVDA",
        "filing_type": "10-K",
        "k": 3,
    }
)
print(f"Results: {len(filing_results)}")
if filing_results:
    first = filing_results[0]
    print(
        f"Top hit: {first.get('ticker')} {first.get('filing_type')} "
        f"{first.get('filing_date')} similarity={first.get('similarity')}"
    )
    print(f"Excerpt: {(first.get('chunk_text') or '')[:200]}...")
else:
    print("WARNING: no filing results returned")

print("\n=== Testing full agent graph ===")
question = (
    "What is NVIDIA's latest revenue and revenue growth, "
    "and what does their 10-K say about data center demand?"
)
result = run_agent(question)
print(f"Model: {result.get('model_used')}")
print(f"Tools executed: {len(result.get('tool_results') or [])}")
print(f"Citations: {len(result.get('citations') or [])}")
print(f"\nAnswer:\n{result.get('answer', '')[:2000]}")
