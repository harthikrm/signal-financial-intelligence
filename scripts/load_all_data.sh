#!/usr/bin/env bash
# One-shot Signal data load against Cloud SQL.
# Run this in YOUR Mac Terminal (not Cursor), and leave it open.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PROXY="$ROOT/.tools/cloud-sql-proxy"
INSTANCE="signal-platform-2026-503720:us-central1:singal-db"
VENV="$ROOT/.venv-ingest311"

if [[ ! -f .env ]]; then
  echo "Missing .env"
  exit 1
fi

# shellcheck disable=SC1091
set -a
source .env
set +a

if [[ -z "${POLYGON_API_KEY_1:-}" ]]; then
  echo "ERROR: POLYGON_API_KEY_1 is empty in .env"
  echo "Add it (and optional POLYGON_API_KEY_2), save, then re-run."
  exit 1
fi

if [[ ! -x "$PROXY" ]]; then
  mkdir -p "$ROOT/.tools"
  curl -sL -o "$PROXY" \
    https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.15.2/cloud-sql-proxy.darwin.arm64
  chmod +x "$PROXY"
fi

if [[ ! -x "$VENV/bin/python" ]]; then
  /opt/homebrew/bin/python3.11 -m venv "$VENV"
  "$VENV/bin/pip" install -U pip
  "$VENV/bin/pip" install -r ingestion/requirements.txt
fi

# Free port + start proxy
lsof -ti tcp:5433 | xargs kill -9 2>/dev/null || true
pkill -9 -f cloud-sql-proxy 2>/dev/null || true
sleep 1
"$PROXY" --gcloud-auth --address 127.0.0.1 --port 5433 "$INSTANCE" \
  > /tmp/signal-sql-proxy.log 2>&1 &
PROXY_PID=$!
echo "Cloud SQL proxy pid=$PROXY_PID"
sleep 4
if ! nc -z 127.0.0.1 5433; then
  echo "Proxy failed to start. Log:"
  cat /tmp/signal-sql-proxy.log
  exit 1
fi

cleanup() {
  echo "Stopping proxy $PROXY_PID"
  kill "$PROXY_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "Ensuring extensions..."
"$VENV/bin/python" - <<'PY'
import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2
conn = psycopg2.connect(
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
)
conn.autocommit = True
cur = conn.cursor()
cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
cur.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
print("extensions ok")
conn.close()
PY

SKIP_FLAG="${1:-}"
echo "Starting ingest... $SKIP_FLAG"
cd ingestion
# Prefer fast path first unless user asked for full
if [[ "$SKIP_FLAG" == "--full" ]]; then
  ../.venv-ingest311/bin/python -u run_initial_load.py
else
  ../.venv-ingest311/bin/python -u run_initial_load.py --skip-embeddings
fi

echo "DONE. Next: run dbt for metrics/indicators."
