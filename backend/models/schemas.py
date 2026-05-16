from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class HealthResponse(BaseModel):
    status: str
    service: str


class ChatQueryRequest(BaseModel):
    question: str
    history: list[dict[str, Any]] = Field(default_factory=list)
    session_id: Optional[str] = Field(default=None, max_length=64)

    @field_validator("question")
    @classmethod
    def validate_question(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("question must not be empty")
        if len(v) > 2000:
            raise ValueError("question exceeds maximum length of 2000 characters")
        return v


class ChatQueryResponse(BaseModel):
    answer: str
    sources: list[str] = Field(default_factory=list)
    model_used: str


class CompareRequest(BaseModel):
    tickers: list[str]

    @field_validator("tickers")
    @classmethod
    def validate_count(cls, v: list[str]) -> list[str]:
        if len(v) < 2:
            raise ValueError("At least 2 tickers required")
        if len(v) > 3:
            raise ValueError("At most 3 tickers allowed")
        return [t.upper().strip() for t in v]


class CompareAnalysisRequest(CompareRequest):
    pass


class CompareResponse(BaseModel):
    content: str
    tickers: list[str]


class CompanyRow(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = None
    exchange: Optional[str] = None
    cik: Optional[str] = None


class MetricsRow(BaseModel):
    model_config = {"extra": "allow"}
    ticker: str
    data: dict[str, Any] = Field(default_factory=dict)


class PriceSummaryRow(BaseModel):
    ticker: str
    last_close: Optional[float] = None
    as_of: Optional[str] = None


class IndicatorRow(BaseModel):
    ticker: str
    date: Optional[str] = None
    rsi_14: Optional[float] = None
    sma_50: Optional[float] = None
    sma_200: Optional[float] = None


class SectorRow(BaseModel):
    sector: str
    company_count: int


class PriceSnapshotItem(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = None
    exchange: Optional[str] = None
    logo_url: Optional[str] = None
    last_close: Optional[float] = None
    day_change_pct: Optional[float] = None
