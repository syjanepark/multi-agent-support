from agents.base_agent import BaseAgent
from graph.state import AgentResponse, GraphState
from config.prompts import GENERAL_SYSTEM_PROMPT


class GeneralAgent(BaseAgent):
    def __init__(self):
        super().__init__(GENERAL_SYSTEM_PROMPT, domain="general")

    def _validate(self, response: AgentResponse, _state: GraphState) -> AgentResponse:
        return response
