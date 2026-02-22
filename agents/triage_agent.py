import json
import structlog
from openai import AzureOpenAI
from graph.state import GraphState, CustomerContext, RoutingDecision
from config.settings import get_settings
from config.prompts import TRIAGE_SYSTEM_PROMPT
from monitoring.cost_tracker import track_tokens

logger = structlog.get_logger()


class TriageAgent:
    """Classifies customer intent and routes to specialized agents."""

    def __init__(self):
        settings = get_settings()
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )
        self.model = settings.azure_openai_mini_deployment  # gpt-5-nano
        self.confidence_threshold = settings.routing_confidence_threshold

    async def process(self, state: GraphState) -> dict:
        logger.info("triage_started", query=state["customer_query"][:100])

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
                {"role": "user", "content": state["customer_query"]},
            ],
            temperature=1,
            response_format={"type": "json_object"},
        )

        usage = response.usage
        token_info = track_tokens(
            "triage",
            usage.prompt_tokens,
            usage.completion_tokens,
            self.model,
        )

        try:
            result = json.loads(response.choices[0].message.content)

            routing = RoutingDecision(
                target_agent=result["target_agent"],
                confidence=result["confidence"],
                reasoning=result["reasoning"],
                requires_escalation=result["confidence"] < self.confidence_threshold,
                escalation_reason=(
                    f"Low confidence: {result['confidence']:.2f}"
                    if result["confidence"] < self.confidence_threshold
                    else None
                ),
            )

            context = CustomerContext(
                intent=result.get("intent"),
                sub_intent=result.get("sub_intent"),
                entities=result.get("entities", {}),
                sentiment=result.get("sentiment", "neutral"),
                urgency=result.get("urgency", "medium"),
            )

            logger.info(
                "triage_complete",
                target=routing.target_agent,
                confidence=routing.confidence,
                intent=context.intent,
            )

            return {
                "customer_context": context,
                "routing_decision": routing,
                "current_agent": routing.target_agent,
                "token_usage": token_info,
            }

        except (json.JSONDecodeError, KeyError) as e:
            logger.error("triage_parse_error", error=str(e))
            return {
                "routing_decision": RoutingDecision(
                    target_agent="general",
                    confidence=0.3,
                    reasoning="Parse error, defaulting to general",
                    requires_escalation=True,
                    escalation_reason=f"Parse error: {str(e)}",
                ),
                "current_agent": "general",
                "error": f"Triage parse error: {str(e)}",
                "token_usage": token_info,
            }