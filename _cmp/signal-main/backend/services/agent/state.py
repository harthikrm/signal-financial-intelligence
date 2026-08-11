from __future__ import annotations

from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    question: str
    refusal: str | None
    plan: list[dict[str, Any]]
    plan_reasoning: str
    tool_results: list[dict[str, Any]]
    verification: dict[str, Any]
    answer: str
    citations: list[str]
    plan_round: int
    max_plan_rounds: int
