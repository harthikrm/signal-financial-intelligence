from fastapi import APIRouter

from models.schemas import CompareAnalysisRequest, CompareRequest, CompareResponse
from services import compare_service

router = APIRouter(prefix="/compare", tags=["compare"], redirect_slashes=False)


@router.post("/", response_model=CompareResponse)
def compare(body: CompareRequest) -> CompareResponse:
    text = compare_service.run_compare(body.tickers)
    return CompareResponse(content=text, tickers=body.tickers)


@router.post("/analysis", response_model=CompareResponse)
def compare_analysis(body: CompareAnalysisRequest) -> CompareResponse:
    out = compare_service.run_compare_json(body.tickers)
    return CompareResponse(content=out["analysis"], tickers=out["tickers"])
