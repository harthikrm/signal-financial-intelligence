# Signal — plan amendments log

Append-only log of approved plan changes (Rule-3).

## Amendments table

| Date       | Change | Reason | Approved by |
|------------|--------|--------|-------------|
| 2026-05-14 | Replace Clearbit Logo API with Logo.dev: `backend/constants.py` — `LOGO_DOMAINS` removed, `LOGO_DEV_BASE_URL` added; `backend/routers/prices.py` — `logo_url` uses Logo.dev ticker URL; `ingestion/config.py` — `LOGO_DOMAINS` removed, comment added; `.env.example` — `LOGO_DEV_TOKEN` added | Clearbit Logo API shut down 2025-12-08. Logo.dev is the official Clearbit-recommended replacement. Ticker-based URL means no domain mapping. `BRK.B` dot-in-ticker verified. Free tier 5000 req/day sufficient for Signal. | Harthik |
| 2026-05-15 | Phase 10 RAG: `langchain_core.messages` used instead of deprecated `langchain.schema` for `HumanMessage` / `SystemMessage` / `AIMessage`. `main.py` maps `RequestValidationError` to HTTP 400 for `/api/chat/query` only (other routes stay 422). `guardrails/rules.py` adds `check_guardrails()` wrapper (same patterns as `guardrail_check` + `political_check`). `query_logger` keeps `tokens_in`/`tokens_out` columns (passed as 0 when unknown). Retrieval `k` for FILING / MULTI_COMPANY overridable via `RAG_K_FILING` / `RAG_K_MULTI_COMPANY`. Classifier `max_tokens` via `CLASSIFIER_MAX_TOKENS`. LLM `max_tokens` / `temperature` via `LLM_MAX_TOKENS` / `LLM_TEMPERATURE`. | Align with current LangChain packages; satisfy FastAPI 400 for invalid chat body; spec import name `check_guardrails`; Rule 1 env-driven limits; preserve existing `query_logs` schema. | Harthik |
| 2026-05-16 | Phase 12 CI: `main.py` — `RequestValidationError` handler uses `jsonable_encoder(exc.errors())` so HTTP 400 responses for `/api/chat/query` are JSON-serializable (Pydantic v2 embeds non-JSON types in `ctx`). Same handler extended to paths ending in `/compare` so `POST /api/compare` body validation (e.g. too many tickers) returns **400** with the same shape, matching `backend/tests/test_endpoints.py`. | Unblocks pytest and GitHub Actions Step 2; prior handler raised `TypeError` on invalid chat body. | Harthik |

## Standing rules (logos)

**Standing rule:** Logo URLs are generated dynamically using the Logo.dev ticker-based API. No static domain mapping exists anywhere in the codebase. `LOGO_DEV_TOKEN` must be set in `.env` and in GCP Cloud Run environment variables before launch.

(Supersedes the prior rule that `LOGO_DOMAINS` existed in two places and had to be kept in sync.)
