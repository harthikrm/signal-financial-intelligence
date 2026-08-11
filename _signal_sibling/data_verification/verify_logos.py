#!/usr/bin/env python3
"""Phase 14 / manual Section 13.2 — render all 70 company logos to logos.html."""

from __future__ import annotations

import os
import sys
import webbrowser
from html import escape

from _common import OUTPUT_DIR, setup_import_paths

LOGOS_HTML = OUTPUT_DIR / "logos.html"


def main() -> int:
    setup_import_paths()
    from config import COMPANIES

    token = os.getenv("LOGO_DEV_TOKEN", "").strip()
    if not token:
        print("ERROR: LOGO_DEV_TOKEN not set in .env", file=sys.stderr)
        return 1

    base = "https://img.logo.dev/ticker"
    parts: list[str] = []
    for c in COMPANIES:
        ticker = c["ticker"]
        src = f"{base}/{ticker}?token={token}"
        parts.append(
            "    <div class=\"tile\">\n"
            f"      <img src=\"{src}\" alt=\"{ticker}\" loading=\"lazy\"\n"
            "           onerror=\"this.classList.add('broken')\"/>\n"
            f"      <div class=\"meta\"><strong>{ticker}</strong>"
            f"<span>{escape(c['name'])}</span>\n"
            f"        <small>{escape(c.get('sector') or '')}</small></div>\n"
            "    </div>"
        )

    n = len(COMPANIES)
    html = (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        "  <meta charset=\"utf-8\"/>\n"
        f"  <title>Signal — Logo verification ({n} companies)</title>\n"
        "  <style>\n"
        "    body { font-family: system-ui, sans-serif; background: #0a0a0a; "
        "color: #eee; margin: 1rem; }\n"
        "    h1 { color: #ff6b00; }\n"
        "    .grid { display: grid; grid-template-columns: "
        "repeat(auto-fill, minmax(140px, 1fr)); gap: 1rem; }\n"
        "    .tile { background: #141414; border: 1px solid #333; "
        "border-radius: 8px; padding: 0.75rem; text-align: center; }\n"
        "    .tile img { width: 64px; height: 64px; object-fit: contain; }\n"
        "    .tile img.broken { opacity: 0.25; border: 2px dashed #c00; }\n"
        "    .meta strong { display: block; }\n"
        "    .meta span { display: block; font-size: 0.75rem; color: #aaa; }\n"
        "  </style>\n</head>\n<body>\n"
        "  <h1>Signal logo spot-check</h1>\n"
        f"  <p>{n} tickers from ingestion/config.py COMPANIES.</p>\n"
        "  <div class=\"grid\">\n"
        + "\n".join(parts)
        + "\n  </div>\n</body>\n</html>\n"
    )

    LOGOS_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote {LOGOS_HTML} ({n} tiles)")
    uri = LOGOS_HTML.as_uri()
    print(f"Open: {uri}")
    if os.getenv("VERIFY_OPEN_BROWSER", "1") == "1":
        webbrowser.open(uri)
    return 0


if __name__ == "__main__":
    sys.exit(main())
