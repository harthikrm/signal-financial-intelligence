from __future__ import annotations

import json
import logging
import os
from typing import Any, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field

from services.agent.prompts import (
    AGENT_SYSTEM_PROMPT,
    PLAN_PROMPT,
    SYNTHESIZE_PROMPT,
    VERIFY_PROMPT,
)
from services.agent.state import AgentState
from services.agent.tickers import (
    allowed_tickers,
    filter_tool_results_by_tickers,
)
from services.agent.tools import (
    TOOL_REGISTRY,
    compare_companies,
    get_company_metrics,
    get_earnings_history,
    get_metrics_history,
    get_price_history,
    search_filings,
)

logger = logging.getLogger(__name__)

TOOL_NAMES = Literal[
    "search_filings",
    "get_company_metrics",
    "compare_companies",
    "get_earnings_history",
    "get_metrics_history",
    "get_price_history",
]


class PlannedTool(BaseModel):
    name: TOOL_NAMES
    args: dict[str, Any] = Field(default_factory=dict)


class PlanOutput(BaseModel):
    tools: list[PlannedTool] = Field(default_factory=list)
    reasoning: str = ""


class VerificationOutput(BaseModel):
    sufficient: bool
    gaps: str = ""


def _llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL_PRODUCTION", "gpt-4o-mini"),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1500")),
        api_key=os.environ.get("OPENAI_API_KEY"),
    )


def _json_dumps(obj: Any) -> str:
    return json.dumps(obj, default=str, indent=2)


def _extract_citations(
    tool_results: list[dict[str, Any]],
    allowed: set[str] | None = None,
) -> list[str]:
    citations: list[str] = []
    seen: set[str] = set()
    for entry in tool_results:
        if entry.get("tool") != "search_filings":
            continue
        result = entry.get("result")
        if not isinstance(result, list):
            continue
        for chunk in result:
            if not isinstance(chunk, dict):
                continue
            ticker = str(chunk.get("ticker", "")).upper()
            if allowed and ticker not in allowed:
                continue
            label = chunk.get("section_label") or "filing excerpt"
            cite = (
                f"{chunk.get('ticker')} {chunk.get('filing_type')} "
                f"{chunk.get('filing_date')}, {label}"
            ).strip()
            if cite and cite not in seen:
                seen.add(cite)
                citations.append(cite)
    return citations


def plan_node(state: AgentState) -> dict[str, Any]:
    prior = state.get("tool_results") or []
    gaps = (state.get("verification") or {}).get("gaps", "")
    prompt = PLAN_PROMPT.format(
        question=state["question"],
        prior_results=_json_dumps(prior) if prior else "[]",
        gaps=gaps or "None",
    )
    llm = _llm().with_structured_output(PlanOutput)
    try:
        plan_out: PlanOutput = llm.invoke(
            [
                SystemMessage(content=AGENT_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]
        )
    except Exception as e:
        logger.exception("plan_node failed: %s", e)
        plan_out = PlanOutput(tools=[], reasoning=f"Planning error: {e}")

    plan = [
        {"name": t.name, "args": t.args}
        for t in plan_out.tools
    ]
    return {
        "plan": plan,
        "plan_reasoning": plan_out.reasoning,
        "plan_round": state.get("plan_round", 0) + 1,
    }


def execute_node(state: AgentState) -> dict[str, Any]:
    plan = state.get("plan") or []
    existing = list(state.get("tool_results") or [])
    round_tag = state.get("plan_round", 1)

    for call in plan:
        name = call.get("name", "")
        args = call.get("args") or {}
        tool = TOOL_REGISTRY.get(name)
        if tool is None:
            existing.append(
                {
                    "round": round_tag,
                    "tool": name,
                    "args": args,
                    "error": "unknown tool",
                }
            )
            continue
        try:
            result = tool.invoke(args)
            existing.append(
                {
                    "round": round_tag,
                    "tool": name,
                    "args": args,
                    "result": result,
                }
            )
        except Exception as e:
            logger.warning("tool %s failed: %s", name, e)
            existing.append(
                {
                    "round": round_tag,
                    "tool": name,
                    "args": args,
                    "error": str(e),
                }
            )

    return {"tool_results": existing}


def verify_node(state: AgentState) -> dict[str, Any]:
    tool_results = state.get("tool_results") or []
    if not tool_results:
        return {
            "verification": {
                "sufficient": False,
                "gaps": "No tool results were returned.",
            }
        }

    prompt = VERIFY_PROMPT.format(
        question=state["question"],
        tool_results=_json_dumps(tool_results),
    )
    llm = _llm().with_structured_output(VerificationOutput)
    try:
        verdict: VerificationOutput = llm.invoke(
            [
                SystemMessage(content=AGENT_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]
        )
    except Exception as e:
        logger.exception("verify_node failed: %s", e)
        verdict = VerificationOutput(
            sufficient=True,
            gaps=f"Verification skipped due to error: {e}",
        )

    return {
        "verification": {
            "sufficient": verdict.sufficient,
            "gaps": verdict.gaps,
        }
    }


def synthesize_node(state: AgentState) -> dict[str, Any]:
    tool_results = state.get("tool_results") or []
    question = state["question"]
    tickers = allowed_tickers(question, tool_results)
    filtered_results = filter_tool_results_by_tickers(tool_results, tickers)
    citations = _extract_citations(filtered_results, tickers)
    prompt = SYNTHESIZE_PROMPT.format(
        question=question,
        tool_results=_json_dumps(filtered_results),
        citations="\n".join(citations) if citations else "None",
    )
    llm = _llm()
    try:
        resp = llm.invoke(
            [
                SystemMessage(content=AGENT_SYSTEM_PROMPT),
                HumanMessage(content=prompt),
            ]
        )
        answer = (resp.content or "").strip()
    except Exception as e:
        logger.exception("synthesize_node failed: %s", e)
        answer = (
            "I could not complete this answer due to a temporary model error. "
            "Please try again shortly."
        )

    if citations and "## Sources" not in answer and "Sources:" not in answer:
        answer = answer + "\n\n**Sources**\n" + "\n".join(f"- {c}" for c in citations)

    return {"answer": answer, "citations": citations}


def route_after_verify(state: AgentState) -> str:
    verification = state.get("verification") or {}
    if verification.get("sufficient"):
        return "synthesize"
    plan_round = state.get("plan_round", 0)
    max_rounds = state.get("max_plan_rounds", 2)
    if plan_round >= max_rounds:
        return "synthesize"
    return "plan"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("plan", plan_node)
    graph.add_node("execute", execute_node)
    graph.add_node("verify", verify_node)
    graph.add_node("synthesize", synthesize_node)

    graph.add_edge(START, "plan")
    graph.add_edge("plan", "execute")
    graph.add_edge("execute", "verify")
    graph.add_conditional_edges(
        "verify",
        route_after_verify,
        {"plan": "plan", "synthesize": "synthesize"},
    )
    graph.add_edge("synthesize", END)
    return graph.compile()


# Re-export tools for graph module introspection / tests
__all__ = [
    "build_graph",
    "search_filings",
    "get_company_metrics",
    "compare_companies",
    "get_earnings_history",
    "get_metrics_history",
    "get_price_history",
]
