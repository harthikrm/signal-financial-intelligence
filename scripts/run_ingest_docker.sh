#!/usr/bin/env bash
# Run initial load in Python 3.11 Docker (avoids local py3.14 / psycopg issues).
# Prerequisites:
#   1. scripts/start_sql_proxy.sh running in another terminal
#   2. .env filled (including POLYGON_API_KEY_1 / _2)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "Missing .env — abort"
  exit 1
fi

# shellcheck disable=SC1091
set -a
# shellcheck source=/dev/null
source .env
set +a

if [[ -z "${POLYGON_API_KEY_1:-}" ]]; then
  echo "POLYGON_API_KEY_1 is empty in .env — add your Polygon key(s) first"
  exit 1
fi

SKIP_FLAG=""
if [[ "${1:-}" == "--skip-embeddings" ]]; then
  SKIP_FLAG="--skip-embeddings"
  echo "Running FAST path (no filings/embeddings)"
fi

echo "Running ingest container (Python 3.11)..."
docker run --rm \
  -v "$ROOT:/work" \
  -w /work/ingestion \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=5433 \
  -e DB_NAME \
  -e DB_USER \
  -e DB_PASSWORD \
  -e OPENAI_API_KEY \
  -e VOYAGE_API_KEY \
  -e POLYGON_API_KEY_1 \
  -e POLYGON_API_KEY_2 \
  -e EDGAR_USER_AGENT_EMAIL \
  python:3.11-slim \
  bash -lc "pip install -q -r requirements.txt && python run_initial_load.py ${SKIP_FLAG}"
