from fastapi import APIRouter

from models.schemas import ChatQueryRequest, ChatQueryResponse
from services.rag_pipeline import answer_query

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/query", response_model=ChatQueryResponse)
def chat_query(body: ChatQueryRequest) -> ChatQueryResponse:
    result = answer_query(body.question, body.history, body.session_id)
    return ChatQueryResponse(
        answer=result["answer"],
        sources=result["sources"],
        model_used=result["model_used"],
    )
