from fastapi import APIRouter

from models.database import db_cursor
from models.schemas import SectorRow

router = APIRouter(prefix="/sectors", tags=["sectors"])


@router.get("/")
def list_sectors() -> list[dict]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT sector, COUNT(*)::int AS n
            FROM companies
            WHERE sector IS NOT NULL AND sector <> ''
            GROUP BY sector
            ORDER BY sector
            """
        )
        rows = cur.fetchall()
    return [SectorRow(sector=r[0], company_count=r[1]).model_dump() for r in rows]
