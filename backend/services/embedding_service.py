import os

import voyageai


def embed_query(text: str) -> list[float]:
    """Embed a single query string for RAG retrieval (voyage-finance-2, query mode)."""
    client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))
    result = client.embed(
        [text],
        model="voyage-finance-2",
        input_type="query",
    )
    return result.embeddings[0]
