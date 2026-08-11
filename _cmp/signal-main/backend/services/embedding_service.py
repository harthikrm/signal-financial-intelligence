import os

import voyageai

_VOYAGE_KEYS = [
    k for k in [
        os.getenv("VOYAGE_API_KEY_1"),
        os.getenv("VOYAGE_API_KEY_2"),
        os.getenv("VOYAGE_API_KEY_3"),
        os.getenv("VOYAGE_API_KEY"),
    ]
    if k and k.strip()
]

_QUOTA_ERROR_WORDS = (
    "quota", "limit", "exceeded", "exhausted",
    "insufficient", "billing", "rate", "429", "402",
)


def _is_quota_error(exc: Exception) -> bool:
    err_str = str(exc).lower()
    return any(word in err_str for word in _QUOTA_ERROR_WORDS)


def embed_query(text: str) -> list[float]:
    """Embed a single query string for RAG retrieval (voyage-finance-2, query mode)."""
    if not _VOYAGE_KEYS:
        raise EnvironmentError(
            "No Voyage AI API keys found. Set VOYAGE_API_KEY_1 in .env"
        )

    last_error = None

    for i, key in enumerate(_VOYAGE_KEYS):
        try:
            client = voyageai.Client(api_key=key.strip())
            result = client.embed(
                [text],
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
