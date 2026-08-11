import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import request_validation_exception_handler
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from models.schemas import HealthResponse
from routers import chat, companies, compare, prices, sectors

load_dotenv()

app = FastAPI(title="Signal API", version="1.0.0")


@app.exception_handler(RequestValidationError)
async def _validation_to_400_for_chat(request: Request, exc: RequestValidationError):
    """Phase 10: Knowledge chat returns 400 for invalid body (per plan)."""
    path = request.url.path.rstrip("/")
    if path.endswith("/chat/query") or path.endswith("/compare"):
        return JSONResponse(
            status_code=400,
            content={"detail": jsonable_encoder(exc.errors())},
        )
    return await request_validation_exception_handler(request, exc)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://signal.harthik.dev",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address, default_limits=["300/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


def require_api_key(request: Request) -> None:
    expected = os.getenv("SIGNAL_API_KEY")
    if not expected:
        return
    got = request.headers.get("X-Signal-Key")
    if got != expected:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="Signal API")


app.include_router(
    companies.router,
    prefix="/api",
    dependencies=[Depends(require_api_key)],
)
app.include_router(
    compare.router,
    prefix="/api",
    dependencies=[Depends(require_api_key)],
)
app.include_router(
    chat.router,
    prefix="/api",
    dependencies=[Depends(require_api_key)],
)
app.include_router(
    sectors.router,
    prefix="/api",
    dependencies=[Depends(require_api_key)],
)
app.include_router(
    prices.router,
    prefix="/api",
    dependencies=[Depends(require_api_key)],
)
