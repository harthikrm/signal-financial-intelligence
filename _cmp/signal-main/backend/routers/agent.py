from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from models.agent_schemas import AgentQueryRequest, AgentQueryResponse
from services.agent.runner import run_agent
from services.agent.streaming import iter_agent_sse

router = APIRouter(prefix="/agent", tags=["agent"], redirect_slashes=False)

_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}


@router.post("/query", response_model=AgentQueryResponse)
def agent_query(body: AgentQueryRequest) -> AgentQueryResponse:
    """Run the agent and return the full result as JSON (non-streaming)."""
    result = run_agent(body.question)
    return AgentQueryResponse(
        answer=result["answer"],
        citations=result.get("citations") or [],
        tool_results=result.get("tool_results") or [],
        plan=result.get("plan") or [],
        plan_reasoning=result.get("plan_reasoning", ""),
        verification=result.get("verification") or {},
        model_used=result["model_used"],
    )


@router.post("/stream")
def agent_stream(body: AgentQueryRequest) -> StreamingResponse:
    """Stream agent progress and final answer via Server-Sent Events."""
    return StreamingResponse(
        iter_agent_sse(body.question),
        media_type="text/event-stream",
        headers=_SSE_HEADERS,
    )
