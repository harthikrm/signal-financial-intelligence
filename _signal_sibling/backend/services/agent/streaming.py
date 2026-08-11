from __future__ import annotations

import json
import os
from collections.abc import Iterator
from typing import Any

from guardrails.rules import check_guardrails

from services.agent.runner import get_graph
from services.agent.state import AgentState


def _sse(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


def _model_used() -> str:
    return os.getenv("LLM_MODEL_PRODUCTION", "gpt-4o-mini")


def _initial_state(question: str) -> AgentState:
    return {
        "question": question.strip(),
        "tool_results": [],
        "plan_round": 0,
        "max_plan_rounds": int(os.getenv("AGENT_MAX_PLAN_ROUNDS", "2")),
    }


def _payload_for_node(node: str, update: dict[str, Any]) -> dict[str, Any]:
    if node == "plan":
        return {
            "plan": update.get("plan") or [],
            "reasoning": update.get("plan_reasoning", ""),
            "round": update.get("plan_round", 0),
        }
    if node == "execute":
        results = update.get("tool_results") or []
        round_num = results[-1].get("round") if results else None
        return {"round": round_num, "tool_results": results}
    if node == "verify":
        return {"verification": update.get("verification") or {}}
    if node == "synthesize":
        return {
            "answer": update.get("answer", ""),
            "citations": update.get("citations") or [],
            "model_used": _model_used(),
        }
    return dict(update)


def iter_agent_sse(question: str) -> Iterator[str]:
    """
    Yield Server-Sent Events for each LangGraph node completion.

    Events: status, plan, tools, verify, done, error
    """
    refusal = check_guardrails(question)
    if refusal:
        yield _sse(
            "done",
            {
                "answer": refusal,
                "citations": [],
                "model_used": "guardrail",
            },
        )
        return

    yield _sse("status", {"stage": "started", "model_used": _model_used()})

    graph = get_graph()
    initial = _initial_state(question)
    accumulated: dict[str, Any] = dict(initial)

    try:
        for chunk in graph.stream(initial, stream_mode="updates"):
            for node, update in chunk.items():
                accumulated.update(update)
                if node == "execute":
                    event_name = "tools"
                elif node == "synthesize":
                    event_name = "done"
                else:
                    event_name = node
                yield _sse(event_name, _payload_for_node(node, update))
    except Exception as exc:
        yield _sse("error", {"message": str(exc)})
        return
