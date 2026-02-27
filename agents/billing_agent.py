from agents.base_agent import BaseAgent
from graph.state import AgentResponse, GraphState
from config.prompts import BILLING_SYSTEM_PROMPT


class BillingAgent(BaseAgent):
    def __init__(self):
        super().__init__(BILLING_SYSTEM_PROMPT, domain="billing")

    def _validate(self, response: AgentResponse, state: GraphState) -> AgentResponse:
        """
        Billing-specific validation:
        - If entities contain an amount > 500, set requires_human=True
        """
        ctx = state.get("customer_context")
        if ctx and ctx.entities:
            raw_amount = ctx.entities.get("amount")
            if raw_amount is not None:
                try:
                    amount = float(raw_amount)
                    if amount > 500 and not response.requires_human:
                        response.requires_human = True
                        response.human_reason = (
                            f"Amount ${amount:.2f} exceeds $500 threshold — requires human review."
                        )
                except (ValueError, TypeError):
                    pass
        return response