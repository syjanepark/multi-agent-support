import time
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from api.schemas import SupportRequest, SupportResponse, HealthResponse
from graph.orchestrator import support_graph
from monitoring.metrics_collector import MetricsCollector

logger = structlog.get_logger()
START_TIME = time.time()
metrics = MetricsCollector()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("app_starting")
    yield
    logger.info("app_shutting_down")


app = FastAPI(
    title="Multi-Agent Customer Support API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/support", response_model=SupportResponse)
async def handle_support(request: SupportRequest):
    request_id = str(uuid.uuid4())
    start = time.time()

    logger.info("request_received", request_id=request_id,
                query_length=len(request.query))

    try:
        config = {"configurable": {"thread_id": request.session_id or request_id}}
        result = await support_graph.ainvoke(
            {
                "customer_query": request.query,
                "messages": [],
                "turn_count": 0,
                "start_time": start,
                "token_usage": {},
                "retrieved_documents": [],
                "conversation_complete": False,
                "customer_context": None,
                "routing_decision": None,
                "current_agent": None,
                "agent_response": None,
                "error": None,
                "final_response": None,
            },
            config=config,
        )

        elapsed = time.time() - start
        routing = result.get("routing_decision")
        agent_resp = result.get("agent_response")
        token_usage = result.get("token_usage") or {}

        was_escalated = bool(
            (routing and routing.requires_escalation)
            or (agent_resp and agent_resp.requires_human)
            or not agent_resp
        )

        response = SupportResponse(
            response=result.get("final_response") or "Unable to process your request.",
            agent_used=result.get("current_agent") or "unknown",
            confidence=agent_resp.confidence if agent_resp else 0.0,
            routing_confidence=routing.confidence if routing else 0.0,
            sources=agent_resp.sources if agent_resp else [],
            suggested_followups=agent_resp.suggested_followups if agent_resp else [],
            was_escalated=was_escalated,
            response_time=round(elapsed, 3),
            cost=token_usage.get("cost", 0.0),
        )

        metrics.record_request(
            request_id=request_id,
            agent_used=response.agent_used,
            routing_confidence=response.routing_confidence,
            response_confidence=response.confidence,
            response_time=response.response_time,
            cost=response.cost,
            escalated=response.was_escalated,
        )

        logger.info("request_complete", request_id=request_id,
                     elapsed=elapsed, agent=response.agent_used)

        return response

    except Exception as e:
        logger.error("request_failed", request_id=request_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        agents=["triage", "billing", "technical", "account", "general"],
        uptime_seconds=round(time.time() - START_TIME, 1),
    )


@app.get("/metrics")
async def get_metrics():
    return metrics.get_summary()