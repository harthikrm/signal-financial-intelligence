#!/usr/bin/env bash
# Start Cloud SQL Auth Proxy on localhost:5433
# Requires: gcloud auth login as hrmallichetty@gmail.com
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROXY="$ROOT/.tools/cloud-sql-proxy"
INSTANCE="signal-platform-2026-503720:us-central1:singal-db"

if [[ ! -x "$PROXY" ]]; then
  echo "Downloading cloud-sql-proxy..."
  mkdir -p "$ROOT/.tools"
  curl -sL -o "$PROXY" \
    https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.15.2/cloud-sql-proxy.darwin.arm64
  chmod +x "$PROXY"
fi

echo "Starting proxy → $INSTANCE on :5433"
exec "$PROXY" --gcloud-auth --address 127.0.0.1 --port 5433 "$INSTANCE"
