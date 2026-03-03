import asyncio
from agents.billing_agent import BillingAgent
from agents.technical_agent import TechnicalAgent
from agents.account_agent import AccountAgent
from agents.general_agent import GeneralAgent

test_cases = [
    (BillingAgent(), "I was charged twice for my subscription this month"),
    (BillingAgent(), "Can I get a refund for $750?"),  # should flag requires_human
    (TechnicalAgent(), "The API keeps returning 429 errors"),
    (TechnicalAgent(), "Is the system down? Nothing is working"),  # should escalate
    (AccountAgent(), "How do I enable 2FA?"),
    (AccountAgent(), "I think my account was hacked"),  # should escalate
    (GeneralAgent(), "What platforms do you support?"),
]


async def main():
    for agent, query in test_cases:
        state = {
            "customer_query": query,
            "messages": [],
            "customer_context": None,  # no triage yet, that's fine
            "turn_count": 0,
            "start_time": 0,
            "token_usage": {},
            "retrieved_documents": [],
            "conversation_complete": False,
        }
        result = await agent.process(state)
        resp = result["agent_response"]
        cost = result["token_usage"]["cost"]
        human = "🚨 ESCALATE" if resp.requires_human else "✓"
        print(f"{human} [{resp.confidence:.2f}] ${cost:.6f} | {query[:50]}")
        print(f"  {resp.content[:100]}...")
        print()

if __name__ == "__main__":
    asyncio.run(main())