"""Phase 3 sanity check: agent JSON + SSE endpoints (server must be running OR use TestClient)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)
API_KEY = __import__("os").getenv("SIGNAL_API_KEY", "")
HEADERS = {"X-Signal-Key": API_KEY} if API_KEY else {}

QUESTION = "What is NVIDIA's latest revenue?"


def _parse_sse(raw: str) -> list[tuple[str, dict]]:
    events: list[tuple[str, dict]] = []
    event_type = None
    for line in raw.split("\n"):
        if line.startswith("event: "):
            event_type = line[7:].strip()
        elif line.startswith("data: ") and event_type:
            events.append((event_type, json.loads(line[6:])))
            event_type = None
    return events


print("=== POST /api/agent/query ===")
resp = client.post(
    "/api/agent/query",
    headers=HEADERS,
    json={"question": QUESTION},
)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    body = resp.json()
    print(f"Model: {body.get('model_used')}")
    print(f"Tools: {len(body.get('tool_results') or [])}")
    print(f"Answer preview: {(body.get('answer') or '')[:300]}...")
else:
    print(resp.text)

print("\n=== POST /api/agent/stream ===")
with client.stream(
    "POST",
    "/api/agent/stream",
    headers=HEADERS,
    json={"question": QUESTION},
) as stream:
    print(f"Status: {stream.status_code}")
    raw = stream.read().decode("utf-8")

events = _parse_sse(raw)
print(f"SSE events: {[e[0] for e in events]}")
done = next((data for name, data in events if name == "done"), None)
if done:
    print(f"Done answer preview: {(done.get('answer') or '')[:300]}...")
