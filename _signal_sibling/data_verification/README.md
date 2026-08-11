# Signal — data verification (Phase 14)

Harthik runs each script, reviews output, and signs off per the build manual before data is trusted in production.

## Setup

From the repo root:

```bash
pip install -r data_verification/requirements.txt
pip install -r backend/requirements.txt   # RAG + embeddings scripts
```

Ensure `.env` has database credentials (`DB_*`), plus keys used by each script:

| Script | Required env |
|--------|----------------|
| `verify_financials.py` | `DB_*` |
| `verify_prices.py` | `DB_*` |
| `verify_logos.py` | `LOGO_DEV_TOKEN` |
| `verify_indicators.py` | `DB_*` |
| `verify_embeddings.py` | `DB_*`, `VOYAGE_API_KEY` |
| `verify_rag.py` | `DB_*`, `OPENAI_API_KEY`, `VOYAGE_API_KEY` |

Optional: `VERIFY_PCT_TOLERANCE` (default `2.0`), `VERIFY_OPEN_BROWSER=0` to skip opening `logos.html`.

## Run order (Tasks 7–12)

```bash
cd data_verification
python verify_financials.py
python verify_prices.py
python verify_logos.py
python verify_indicators.py
python verify_embeddings.py
python verify_rag.py
```

Scripts expect **ingested data + dbt marts** on the database pointed to by `.env` (local Docker Postgres or Cloud SQL via proxy). Task 7 in the manual may follow Phase 16 initial load; partial data is OK — scripts print `SKIP` where rows are missing.

## Outputs

- Console tables for financials, prices, indicators, embeddings, RAG
- `logos.html` (gitignored) — visual review of all 70 Logo.dev tiles

## Sign-off phrases

- Financials: **"Financials verified."**
- Prices: **"Prices verified."**
- Logos: **"Logos verified."**
- Indicators: **"Indicators verified."**
- Embeddings: **"Embeddings verified."**
- RAG: **"RAG verified."**

Phase gate: **"Phase 14 complete. Proceed to Phase 15."**
