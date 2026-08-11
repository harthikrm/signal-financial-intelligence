"""Shared helpers for data_verification scripts (Phase 14)."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from contextlib import contextmanager
from typing import Any, Generator

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(__file__).resolve().parent

load_dotenv(REPO_ROOT / ".env")


def setup_import_paths() -> None:
    """Allow imports from `backend/` and `ingestion/`."""
    for p in (REPO_ROOT, REPO_ROOT / "backend", REPO_ROOT / "ingestion"):
        s = str(p)
        if s not in sys.path:
            sys.path.insert(0, s)


def pct_tolerance() -> float:
    return float(os.getenv("VERIFY_PCT_TOLERANCE", "2.0"))


def abs_tolerance() -> float:
    return float(os.getenv("VERIFY_ABS_TOLERANCE", "1e-6"))


def rel_diff_pct(signal_val: float | None, ref_val: float | None) -> float | None:
    if signal_val is None or ref_val is None:
        return None
    if ref_val == 0:
        return None if signal_val == 0 else float("inf")
    return abs(signal_val - ref_val) / abs(ref_val) * 100.0


def pass_fail(diff_pct: float | None, label: str) -> str:
    tol = pct_tolerance()
    if diff_pct is None:
        return f"{label}: SKIP (missing value)"
    if diff_pct <= tol:
        return f"{label}: PASS ({diff_pct:.2f}% diff, tol {tol}%)"
    return f"{label}: FAIL ({diff_pct:.2f}% diff, tol {tol}%)"


@contextmanager
def db_cursor() -> Generator[Any, None, None]:
    setup_import_paths()
    from models.database import db_cursor as _db_cursor

    with _db_cursor() as cur:
        yield cur
