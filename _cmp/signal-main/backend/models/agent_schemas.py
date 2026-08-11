from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class AgentQueryRequest(BaseModel):
    question: str
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


class AgentQueryResponse(BaseModel):
    answer: str
    citations: list[str] = Field(default_factory=list)
    tool_results: list[dict[str, Any]] = Field(default_factory=list)
    plan: list[dict[str, Any]] = Field(default_factory=list)
    plan_reasoning: str = ""
    verification: dict[str, Any] = Field(default_factory=dict)
    model_used: str
