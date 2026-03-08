from pydantic import BaseModel, Field
from typing import Optional


class SupportRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    customer_id: Optional[str] = None
    session_id: Optional[str] = None


class SupportResponse(BaseModel):
    response: str
    agent_used: str
    confidence: float
    routing_confidence: float
    sources: list[str]
    suggested_followups: list[str]
    was_escalated: bool
    response_time: float
    cost: float


class HealthResponse(BaseModel):
    status: str
    version: str
    agents: list[str]
    uptime_seconds: float