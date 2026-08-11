import os

from fastapi import APIRouter

from constants import LOGO_DEV_BASE_URL
from models.database import db_cursor
from models.schemas import PriceSnapshotItem

router = APIRouter(prefix="/prices", tags=["prices"])

LOGO_DEV_TOKEN = os.getenv("LOGO_DEV_TOKEN", "")


def _logo_url(ticker: str) -> str | None:
    if not LOGO_DEV_TOKEN:
        return None
    return f"{LOGO_DEV_BASE_URL}/{ticker}?token={LOGO_DEV_TOKEN}"


@router.get("/snapshot")
def snapshot() -> list[dict]:
    with db_cursor() as cur:
        cur.execute(
            """
            WITH ranked AS (
                SELECT
                    d.ticker,
                    d.close,
                    ROW_NUMBER() OVER (
                        PARTITION BY d.ticker
                        ORDER BY d.date DESC NULLS LAST
                    ) AS rn
                FROM price_daily d
            )
            SELECT
                c.ticker,
                c.name,
                c.sector,
                c.exchange,
                r1.close AS last_close,
                r2.close AS prev_close
            FROM companies c
            LEFT JOIN ranked r1
                ON r1.ticker = c.ticker AND r1.rn = 1
            LEFT JOIN ranked r2
                ON r2.ticker = c.ticker AND r2.rn = 2
            ORDER BY c.ticker
            """
        )
        rows = cur.fetchall()
    out: list[dict] = []
    for r in rows:
        ticker, name, sector, exchange, last_c, prev_c = (
            r[0],
            r[1],
            r[2],
            r[3],
            r[4],
            r[5],
        )
        day_pct: float | None = None
        if last_c is not None and prev_c is not None and float(prev_c) != 0:
            day_pct = (float(last_c) - float(prev_c)) / float(prev_c) * 100.0
        out.append(
            PriceSnapshotItem(
                ticker=ticker,
                name=name,
                sector=sector,
                exchange=exchange,
                logo_url=_logo_url(ticker),
                last_close=float(last_c) if last_c is not None else None,
                day_change_pct=day_pct,
            ).model_dump()
        )
    return out
