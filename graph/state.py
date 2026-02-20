from typing import Annotated, Literal, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


class CustomerContext(BaseModel):
    """Extracted context about the customer query."""
    customer_id: Optional[str] = None
    intent: Optional[str] = None
    sub_intent: Optional[str] = None
    entities: dict = Field(default_factory=dict)
    sentiment: Optional[str] = None
    urgency: Literal["low", "medium", "high", "critical"] = "medium"


class RoutingDecision(BaseModel):
    """Triage agent routing decision."""
    target_agent: Literal["billing", "technical", "account", "general"]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str = ""
    requires_escalation: bool = False
    escalation_reason: Optional[str] = None


class AgentResponse(BaseModel):
    """Standardized response from any specialized agent."""
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    sources: list[str] = Field(default_factory=list)
    suggested_followups: list[str] = Field(default_factory=list)
    requires_human: bool = False
    human_reason: Optional[str] = None


class GraphState(TypedDict):
    """Shared state across all agents."""
    messages: list[dict]
    customer_query: str
    customer_context: Optional[CustomerContext]
    routing_decision: Optional[RoutingDecision]
    current_agent: Optional[str]
    agent_response: Optional[AgentResponse]
    retrieved_documents: list[dict]
    turn_count: int
    start_time: float
    token_usage: dict
    error: Optional[str]
    final_response: Optional[str]
    conversation_complete: bool