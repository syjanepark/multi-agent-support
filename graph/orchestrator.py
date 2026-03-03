from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import GraphState
from graph.nodes import (
    triage_node, billing_node, technical_node,
    account_node, general_node, synthesize_node, escalation_node
)
from graph.edges import route_after_triage, route_after_agent


def build_support_graph():
    graph = StateGraph(GraphState)

    # Nodes
    graph.add_node("triage", triage_node)
    graph.add_node("billing", billing_node)
    graph.add_node("technical", technical_node)
    graph.add_node("account", account_node)
    graph.add_node("general", general_node)
    graph.add_node("synthesize", synthesize_node)
    graph.add_node("escalation", escalation_node)

    # Entry point
    graph.set_entry_point("triage")

    # Triage routes to one of 5 targets
    graph.add_conditional_edges(
        "triage",
        route_after_triage,
        {
            "billing": "billing",
            "technical": "technical",
            "account": "account",
            "general": "general",
            "escalation": "escalation",
        },
    )

    # Each agent routes to synthesize or escalation
    for agent in ("billing", "technical", "account", "general"):
        graph.add_conditional_edges(
            agent,
            route_after_agent,
            {"synthesize": "synthesize", "escalation": "escalation"},
        )

    # Terminal edges
    graph.add_edge("synthesize", END)
    graph.add_edge("escalation", END)

    return graph.compile(checkpointer=MemorySaver())


support_graph = build_support_graph()
