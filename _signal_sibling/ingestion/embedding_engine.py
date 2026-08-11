import os
import re

import voyageai
from config import CHUNK_SIZE_TOKENS, CHUNK_OVERLAP_TOKENS

# Multi-key failover — tries keys in order when quota is exhausted
_VOYAGE_KEYS = [
    k for k in [
        os.getenv("VOYAGE_API_KEY_1"),
        os.getenv("VOYAGE_API_KEY_2"),
        os.getenv("VOYAGE_API_KEY_3"),
        os.getenv("VOYAGE_API_KEY"),   # legacy fallback
    ]
    if k and k.strip()
]

if not _VOYAGE_KEYS:
    raise EnvironmentError(
        "No Voyage AI API keys found. Set VOYAGE_API_KEY_1 in .env"
    )

_QUOTA_ERROR_WORDS = (
    "quota", "limit", "exceeded", "exhausted",
    "insufficient", "billing", "rate", "429", "402",
)

FILING_SECTIONS = [
    "Item 1",   # Business
    "Item 1A",  # Risk Factors
    "Item 1B",  # Unresolved Staff Comments
    "Item 2",   # Properties
    "Item 7",   # MD&A
    "Item 7A",  # Quantitative Disclosures
    "Item 8",   # Financial Statements
]


def _is_quota_error(exc: Exception) -> bool:
    err_str = str(exc).lower()
    return any(word in err_str for word in _QUOTA_ERROR_WORDS)


def chunk_filing(filing_text: str, ticker: str,
                 filing_type: str, filing_date: str,
                 fiscal_year: int = None,
                 fiscal_quarter: str = None) -> list:
    """
    Hybrid chunking strategy:
    1. Split by filing section (Item 1, 1A, 7, 8, etc.)
    2. Within each section, chunk at CHUNK_SIZE_TOKENS with overlap
    Returns list of chunk dicts with metadata.
    """
    sections = _split_by_section(filing_text)
    chunks   = []

    for section_label, section_text in sections.items():
        words      = section_text.split()
        chunk_size = CHUNK_SIZE_TOKENS
        overlap    = CHUNK_OVERLAP_TOKENS
        start      = 0
        idx        = 0

        while start < len(words):
            end         = min(start + chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text  = " ".join(chunk_words)

            chunks.append({
                "ticker":          ticker,
                "filing_type":     filing_type,
                "filing_date":     filing_date,
                "fiscal_year":     fiscal_year,
                "fiscal_quarter":  fiscal_quarter,
                "section_label":   section_label,
                "chunk_index":     idx,
                "chunk_text":      chunk_text,
                "token_count":     len(chunk_words),
            })
            start += chunk_size - overlap
            idx   += 1

    return chunks


def embed_chunks(chunks: list) -> list:
    """
    Embed a list of chunk dicts using voyage-finance-2.
    Automatically fails over to next API key when quota is exhausted.

    Each chunk dict must have: text or chunk_text, section_label, chunk_index
    Returns list of chunk dicts with embedding field added.
    """
    if not chunks:
        return []

    batch_size = 128
    last_error = None

    for i, key in enumerate(_VOYAGE_KEYS):
        try:
            client = voyageai.Client(api_key=key.strip())
            embedded = []
            for start in range(0, len(chunks), batch_size):
                batch = chunks[start:start + batch_size]
                texts = [c.get("text") or c.get("chunk_text") for c in batch]
                result = client.embed(
                    texts,
                    model="voyage-finance-2",
                    input_type="document",
                )
                for chunk, embedding in zip(batch, result.embeddings):
                    embedded.append({**chunk, "embedding": embedding})
            return embedded
        except Exception as e:
            if _is_quota_error(e):
                print(
                    f"[embedding] Key {i + 1} exhausted or rate limited, "
                    "trying next key..."
                )
                last_error = e
                continue
            raise

    raise Exception(
        f"All {len(_VOYAGE_KEYS)} Voyage AI API keys exhausted or failed. "
        f"Last error: {last_error}"
    )


def embed_query(query_text: str) -> list:
    """
    Embed a single query string for RAG retrieval.
    Uses query input_type for better retrieval alignment.
    """
    last_error = None

    for i, key in enumerate(_VOYAGE_KEYS):
        try:
            client = voyageai.Client(api_key=key.strip())
            result = client.embed(
                [query_text],
                model="voyage-finance-2",
                input_type="query",
            )
            return result.embeddings[0]
        except Exception as e:
            if _is_quota_error(e):
                print(
                    f"[embedding] Key {i + 1} exhausted or rate limited, "
                    "trying next key..."
                )
                last_error = e
                continue
            raise

    raise Exception(
        f"All {len(_VOYAGE_KEYS)} Voyage AI API keys exhausted or failed. "
        f"Last error: {last_error}"
    )


def _split_by_section(text: str) -> dict:
    """
    Split 10-K/10-Q text by Item sections.
    Returns dict of {section_label: section_text}.
    Falls back to full text if sections not found.
    """
    sections = {}
    pattern  = r"(Item\s+\d+[A-Z]?\.?\s+[A-Z][^\n]{0,80})"
    parts    = re.split(pattern, text, flags=re.IGNORECASE)

    if len(parts) <= 1:
        return {"Full Document": text}

    current_label = "Preamble"
    current_text  = []

    for part in parts:
        if re.match(pattern, part, re.IGNORECASE):
            if current_text:
                sections[current_label] = " ".join(current_text)
            current_label = part.strip()
            current_text  = []
        else:
            current_text.append(part)

    if current_text:
        sections[current_label] = " ".join(current_text)

    return sections
