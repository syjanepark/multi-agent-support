import structlog

logger = structlog.get_logger()

PRICING = {
    "gpt-5-mini": {"input": 0.00025, "output": 0.002},
    "gpt-5-nano": {"input": 0.00005, "output": 0.0004},
    "text-embedding-3-small": {"input": 0.00002, "output": 0.0},
}


def track_tokens(agent_name, input_tokens, output_tokens, model):
    prices = PRICING.get(model, PRICING["gpt-5-nano"])
    cost = (
        (input_tokens / 1_000) * prices["input"]
        + (output_tokens / 1_000) * prices["output"]
    )
    logger.info(
        "token_usage",
        agent=agent_name,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost=f"${cost:.6f}",
    )
    return {
        "agent": agent_name,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": cost,
    }