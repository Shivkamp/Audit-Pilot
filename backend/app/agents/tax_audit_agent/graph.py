from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agents.tax_audit_agent.nodes import (
    classify_intent_node,
    evidence_search_node,
    generate_grounded_answer_node,
    risk_explanation_node,
    risk_listing_node,
    risk_summary_node,
    route_intent,
    source_trace_node,
    unsupported_node,
    validate_citations_node,
    validate_request_node,
)
from app.agents.tax_audit_agent.state import TaxAuditAgentState
from app.agents.tax_audit_agent.tools import TaxAuditAgentTools
from app.llm.service import LLMService


def build_tax_audit_agent_graph(
    *,
    tools: TaxAuditAgentTools,
    llm_service: LLMService,
):
    graph = StateGraph(TaxAuditAgentState)

    graph.add_node("validate_request", lambda state: validate_request_node(state, tools=tools))
    graph.add_node("classify_intent", lambda state: classify_intent_node(state, llm_service=llm_service))
    graph.add_node("risk_summary", lambda state: risk_summary_node(state, tools=tools))
    graph.add_node("risk_listing", lambda state: risk_listing_node(state, tools=tools))
    graph.add_node("risk_explanation", lambda state: risk_explanation_node(state, tools=tools))
    graph.add_node("evidence_search", lambda state: evidence_search_node(state, tools=tools))
    graph.add_node("source_trace", lambda state: source_trace_node(state, tools=tools))
    graph.add_node("unsupported", unsupported_node)
    graph.add_node(
        "generate_grounded_answer",
        lambda state: generate_grounded_answer_node(state, llm_service=llm_service),
    )
    graph.add_node("validate_citations", validate_citations_node)

    graph.set_entry_point("validate_request")
    graph.add_edge("validate_request", "classify_intent")

    graph.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "risk_summary": "risk_summary",
            "risk_listing": "risk_listing",
            "risk_explanation": "risk_explanation",
            "evidence_search": "evidence_search",
            "source_trace": "source_trace",
            "unsupported": "unsupported",
        },
    )

    graph.add_edge("risk_summary", "generate_grounded_answer")
    graph.add_edge("risk_listing", "generate_grounded_answer")
    graph.add_edge("risk_explanation", "generate_grounded_answer")
    graph.add_edge("evidence_search", "generate_grounded_answer")
    graph.add_edge("source_trace", "generate_grounded_answer")
    graph.add_edge("unsupported", "generate_grounded_answer")
    graph.add_edge("generate_grounded_answer", "validate_citations")
    graph.add_edge("validate_citations", END)

    return graph.compile()
