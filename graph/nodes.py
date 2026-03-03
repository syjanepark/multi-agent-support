import time
import structlog
from agents.triage_agent import TriageAgent
from agents.billing_agent import BillingAgent
from agents.technical_agent import TechnicalAgent
from agents.account_agent import AccountAgent
from agents.general_agent import GeneralAgent
from agents.response_synthesizer import ResponseSynthesizer
from graph.state import GraphState

logger = structlog.get_logger()

# Singletons — initialized once, reused across requests
triage = TriageAgent()
billing = BillingAgent()
technical = TechnicalAgent()
account = AccountAgent()
general = GeneralAgent()
synthesizer = ResponseSynthesizer()


async def triage_node(state: GraphState) -> dict:
    return await triage.process(state)


async def billing_node(state: GraphState) -> dict:
    return await billing.process(state)


async def technical_node(state: GraphState) -> dict:
    return await technical.process(state)


async def account_node(state: GraphState) -> dict:
    return await account.process(state)


async def general_node(state: GraphState) -> dict:
    return await general.process(state)


async def synthesize_node(state: GraphState) -> dict:
    result = await synthesizer.process(state)
    elapsed = round(time.time() - state["start_time"], 3)
    logger.info("request_complete", elapsed_seconds=elapsed)
    result["elapsed_seconds"] = elapsed
    return result


async def escalation_node(state: GraphState) -> dict:
    routing = state.get("routing_decision")
    agent_response = state.get("agent_response")

    # Collect escalation reasons from both routing and agent validation
    reasons = []
    if routing and routing.escalation_reason:
        reasons.append(routing.escalation_reason)
    if agent_response and agent_response.human_reason:
        reasons.append(agent_response.human_reason)
    reason = "; ".join(reasons) or "This query requires human assistance."

    # Build customer-facing message, including any partial agent content
    message = (
        "Thank you for reaching out. Your request has been escalated to our support team "
        "and a human agent will follow up with you shortly.\n\n"
    )
    if agent_response and agent_response.content:
        message += f"{agent_response.content}\n\n"
    message += f"Escalation reason: {reason}"

    logger.info("escalation_triggered", agent=state.get("current_agent"), reason=reason)

    return {"final_response": message, "conversation_complete": True}
