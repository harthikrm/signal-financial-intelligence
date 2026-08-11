from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from guardrails.rules import check_guardrails

from services.agent.graph import build_graph
from services.agent.state import AgentState

load_dotenv()

_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph


def run_agent(
    question: str,
    *,
    max_plan_rounds: int | None = None,
) -> dict[str, Any]:
    """
    Run the Signal Agent LangGraph workflow (plan → execute → verify → synthesize).

    Returns dict with: answer, citations, tool_results, plan, verification, model_used
    """
    refusal = check_guardrails(question)
    if refusal:
        return {
            "answer": refusal,
            "citations": [],
            "tool_results": [],
            "plan": [],
            "verification": {"sufficient": True, "gaps": ""},
            "model_used": "guardrail",
        }

    rounds = max_plan_rounds
    if rounds is None:
        rounds = int(os.getenv("AGENT_MAX_PLAN_ROUNDS", "2"))

    initial: AgentState = {
        "question": question.strip(),
        "tool_results": [],
        "plan_round": 0,
        "max_plan_rounds": rounds,
    }

    final = get_graph().invoke(initial)
    model_used = os.getenv("LLM_MODEL_PRODUCTION", "gpt-4o-mini")

    return {
        "answer": final.get("answer", ""),
        "citations": final.get("citations") or [],
        "tool_results": final.get("tool_results") or [],
        "plan": final.get("plan") or [],
        "plan_reasoning": final.get("plan_reasoning", ""),
        "verification": final.get("verification") or {},
        "model_used": model_used,
    }
