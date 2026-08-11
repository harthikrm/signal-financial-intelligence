#!/usr/bin/env python3
"""
Phase 14 — pgvector semantic-search spot-check on embeddings table.
"""

from __future__ import annotations

import sys

from _common import db_cursor, setup_import_paths

# (query, optional ticker filter, min expected similarity if rows exist)
TEST_QUERIES: list[tuple[str, str | None]] = [
    (
        "What are the principal risk factors described in NVIDIA's 10-K?",
        "NVDA",
    ),
    (
        "Microsoft revenue growth and cloud segment discussion in SEC filings",
        "MSFT",
    ),
    (
        "Tesla Cybertruck production risks and manufacturing challenges",
        "TSLA",
    ),
]

TOP_K = 5


def _search(query: str, ticker: str | None) -> list[tuple]:
    setup_import_paths()
    from services.embedding_service import embed_query

    vec = embed_query(query)
    vec_literal = "[" + ",".join(str(float(x)) for x in vec) + "]"
    with db_cursor() as cur:
        if ticker:
            cur.execute(
                """
                SELECT ticker, filing_type, filing_date::text, section_label,
                       left(chunk_text, 120) AS preview,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM embeddings
                WHERE ticker = %s AND embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (vec_literal, ticker, vec_literal, TOP_K),
            )
        else:
            cur.execute(
                """
                SELECT ticker, filing_type, filing_date::text, section_label,
                       left(chunk_text, 120) AS preview,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM embeddings
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (vec_literal, vec_literal, TOP_K),
            )
        return cur.fetchall()


def main() -> int:
    setup_import_paths()
    if not __import__("os").getenv("VOYAGE_API_KEY"):
        print("ERROR: VOYAGE_API_KEY required", file=sys.stderr)
        return 1

    print("Embedding semantic search spot-check (top-k=%d)\n" % TOP_K)
    empty = 0
    for query, ticker in TEST_QUERIES:
        print("=" * 72)
        print(f"QUERY: {query}")
        if ticker:
            print(f"FILTER: ticker={ticker}")
        try:
            rows = _search(query, ticker)
        except Exception as exc:
            print(f"ERROR: {exc}")
            empty += 1
            continue
        if not rows:
            print("  (no embedding rows — run ingestion embed step first)")
            empty += 1
            continue
        for i, r in enumerate(rows, 1):
            sim = float(r[5]) if r[5] is not None else 0.0
            print(
                f"  {i}. [{sim:.3f}] {r[0]} {r[1]} {r[2]} — {r[3] or 'section'}"
            )
            print(f"     {r[4]}...")
        print()
    if empty == len(TEST_QUERIES):
        print("RESULT: no embeddings to verify — load data first")
        return 2
    print("RESULT: review top chunks above for semantic alignment (Harthik sign-off)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
