def route_after_triage(state) -> str:
    """
    Return one of: "billing", "technical", "account", "general", "escalation"

    Logic:
    - No routing decision? -> escalation
    - requires_escalation is True? -> escalation
    - Otherwise -> routing_decision.target_agent
    """
    routing = state.get("routing_decision")
    if not routing or routing.requires_escalation:
        return "escalation"
    return routing.target_agent


def route_after_agent(state) -> str:
    """
    Return one of: "synthesize", "escalation"

    Logic:
    - No agent_response? -> escalation
    - requires_human is True? -> escalation
    - confidence < 0.5? -> escalation
    - Otherwise -> synthesize
    """
    agent_response = state.get("agent_response")
    if not agent_response:
        print("  -> escalation: no agent_response")
        return "escalation"
    if agent_response.requires_human:
        print(f"  -> escalation: requires_human ({agent_response.human_reason})")
        return "escalation"
    if agent_response.confidence < 0.5:
        print(f"  -> escalation: low confidence ({agent_response.confidence})")
        return "escalation"
    return "synthesize"
