from agents.base_agent import BaseAgent
from graph.state import AgentResponse, GraphState
from config.prompts import TECHNICAL_SYSTEM_PROMPT


class TechnicalAgent(BaseAgent):
    def __init__(self):
        super().__init__(TECHNICAL_SYSTEM_PROMPT, domain="technical")

    def _validate(self, response: AgentResponse, state: GraphState) -> AgentResponse:
        """
        Technical-specific validation:
        - If query mentions "outage" or "down", set requires_human=True
        """
        query = state.get("customer_query", "").lower()
        if any(keyword in query for keyword in ("outage", "down")):
            if not response.requires_human:
                response.requires_human = True
                response.human_reason = "Query indicates a potential outage or service disruption — requires human review."
        return response