import json
import structlog
from openai import AzureOpenAI
from graph.state import GraphState, AgentResponse
from config.settings import get_settings
from monitoring.cost_tracker import track_tokens
from tools.rag_tool import RAGTool

logger = structlog.get_logger()


class BaseAgent:
    """Base class for all specialized agents."""

    def __init__(self, system_prompt: str, domain: str):
        settings = get_settings()
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )
        self.model = settings.azure_openai_chat_deployment  # gpt-5-mini
        self.system_prompt = system_prompt
        self.domain = domain
        self.rag = RAGTool(domain=self.domain)

    async def process(self, state: GraphState) -> dict:
        """
        Process a customer query. Steps:
        1. Retrieve relevant docs using RAG (filtered by self.domain)
        2. Build the prompt with: system prompt, customer query,
           customer context (sentiment, urgency, entities), and retrieved docs
        3. Call gpt-5-mini with response_format=json_object
        4. Parse into AgentResponse
        5. Run domain-specific validation (override _validate method)
        6. Track tokens and return result
        """
        logger.info("agent_started", domain=self.domain, query=state["customer_query"][:100])

        # 1. Retrieve relevant docs
        docs = await self.rag.retrieve(state["customer_query"])

        # 2. Build user message with query, context, and docs
        context_str = self._build_context_string(state)
        docs_str = ""
        if docs:
            docs_str = "\n\nRelevant documentation:\n" + "\n\n".join(
                f"[{d.get('source', 'unknown')}]\n{d.get('content', '')}" for d in docs
            )

        user_message = f"{state['customer_query']}\n\n{context_str}{docs_str}"

        # 3. Call gpt-5-mini with json_object response format
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=1,
            response_format={"type": "json_object"},
        )

        usage = response.usage
        token_info = track_tokens(
            self.domain,
            usage.prompt_tokens,
            usage.completion_tokens,
            self.model,
        )

        # 4. Parse into AgentResponse
        try:
            result = json.loads(response.choices[0].message.content)
            agent_response = AgentResponse(
                content=result["content"],
                confidence=result.get("confidence", 0.5),
                sources=result.get("sources", []),
                suggested_followups=result.get("suggested_followups", []),
                requires_human=result.get("requires_human", False),
                human_reason=result.get("human_reason"),
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.error("agent_parse_error", domain=self.domain, error=str(e))
            agent_response = AgentResponse(
                content="I'm sorry, I encountered an error processing your request. Please try again.",
                confidence=0.0,
                requires_human=True,
                human_reason=f"Parse error: {str(e)}",
            )

        # 5. Domain-specific validation
        agent_response = self._validate(agent_response, state)

        logger.info(
            "agent_complete",
            domain=self.domain,
            confidence=agent_response.confidence,
            requires_human=agent_response.requires_human,
        )

        # 6. Return result
        return {
            "agent_response": agent_response,
            "retrieved_documents": docs,
            "token_usage": token_info,
        }

    def _build_context_string(self, state: GraphState) -> str:
        """Build a context string from customer context."""
        ctx = state.get("customer_context")
        if not ctx:
            return ""

        parts = []
        if ctx.sentiment:
            parts.append(f"Customer sentiment: {ctx.sentiment}")
        if ctx.urgency:
            parts.append(f"Urgency: {ctx.urgency}")
        if ctx.entities:
            entities_str = ", ".join(f"{k}: {v}" for k, v in ctx.entities.items())
            parts.append(f"Entities: {entities_str}")

        if not parts:
            return ""

        return "Customer context:\n" + "\n".join(parts)

    def _validate(self, response: AgentResponse, state: GraphState) -> AgentResponse:
        """Override in subclasses for domain-specific validation."""
        return response
