from agents.base_agent import BaseAgent
from graph.state import AgentResponse, GraphState
from config.prompts import ACCOUNT_SYSTEM_PROMPT


class AccountAgent(BaseAgent):
    def __init__(self):
        super().__init__(ACCOUNT_SYSTEM_PROMPT, domain="account")

    def _validate(self, response: AgentResponse, state: GraphState) -> AgentResponse:
        """
        Account-specific validation:
        - If query mentions "breach", "hacked", or "locked out", set requires_human=True
        """
        query = state.get("customer_query", "").lower()
        if any(keyword in query for keyword in ("breach", "hacked", "locked out")):
            if not response.requires_human:
                response.requires_human = True
                response.human_reason = "Query indicates a potential security incident — requires human review."
        return response
