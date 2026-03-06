import structlog
from openai import AsyncAzureOpenAI
from graph.state import GraphState
from config.settings import get_settings
from config.prompts import SYNTHESIZER_PROMPT
from monitoring.cost_tracker import track_tokens

logger = structlog.get_logger()


class ResponseSynthesizer:
    def __init__(self):
        settings = get_settings()
        self.client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )
        self.model = settings.azure_openai_mini_deployment  # gpt-5-nano (cheap)

    async def process(self, state: GraphState) -> dict:
        """
        Take the agent_response and customer_context from state.
        Ask the LLM to rewrite the response considering:
        - Customer sentiment and urgency
        - Professional tone
        - Include sources as references
        - Add suggested follow-up questions

        Return: {"final_response": "...", "conversation_complete": True}
        """
        agent_response = state.get("agent_response")
        ctx = state.get("customer_context")

        # Build agent context block
        context_parts = [f"Raw response: {agent_response.content}"]
        if agent_response.sources:
            context_parts.append("Sources: " + ", ".join(agent_response.sources))
        if agent_response.suggested_followups:
            context_parts.append("Suggested follow-ups: " + "; ".join(agent_response.suggested_followups))
        agent_context_str = "\n".join(context_parts)

        sentiment = ctx.sentiment if ctx else "neutral"
        urgency = ctx.urgency if ctx else "medium"

        user_message = (
            f"Customer Query: {state['customer_query']}\n\n"
            f"Agent Context:\n{agent_context_str}\n\n"
            f"Sentiment: {sentiment}\n"
            f"Urgency: {urgency}"
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYNTHESIZER_PROMPT},
                {"role": "user", "content": user_message},
            ],
            max_completion_tokens=300,
        )

        usage = response.usage
        track_tokens("synthesizer", usage.prompt_tokens, usage.completion_tokens, self.model)

        final_response = response.choices[0].message.content.strip()

        logger.info("synthesizer_complete", chars=len(final_response))

        return {"final_response": final_response, "conversation_complete": True}