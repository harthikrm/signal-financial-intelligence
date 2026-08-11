#!/usr/bin/env python3
"""
Phase 14 / manual Section 13.4 — five verbatim RAG quality questions.
"""

from __future__ import annotations

import sys

from _common import setup_import_paths

# Byte-identical to backend/tests/test_model_comparison.py QUESTIONS
QUESTIONS = [
    "What are the top 3 risk factors for NVIDIA based on their most recent 10-K?",
    "How has Microsoft's revenue grown over the last 3 years?",
    "What is free cash flow and why does it matter?",
    "Compare Apple and Google's operating margins based on their filings",
    "What did Tesla say about Cybertruck production in their latest 10-K?",
]


def main() -> int:
    setup_import_paths()
    import os

    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY required", file=sys.stderr)
        return 1

    from services.rag_pipeline import answer_query

    print("Signal RAG pipeline — five manual test questions\n")
    for idx, question in enumerate(QUESTIONS, start=1):
        print("=" * 72)
        print(f"Q{idx}: {question}")
        print("-" * 72)
        try:
            out = answer_query(question, history=[], session_id="verify-rag")
        except Exception as exc:
            print(f"ERROR: {exc}\n")
            continue
        print(f"model_used: {out.get('model_used')}")
        print(f"\nANSWER:\n{out.get('answer')}\n")
        sources = out.get("sources") or []
        if sources:
            print("SOURCES:")
            for s in sources:
                print(f"  - {s}")
        else:
            print("SOURCES: (none)")
        print()
    print("RESULT: Harthik reviews each answer vs manual expectations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
