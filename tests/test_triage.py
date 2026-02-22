import asyncio
from agents.triage_agent import TriageAgent

agent = TriageAgent()

test_queries = [
    # Should route to billing
    ("I was charged twice for my subscription this month", "billing"),
    ("Can I get a refund for my last payment?", "billing"),
    ("What's the pricing for the enterprise plan?", "billing"),

    # Should route to technical
    ("The API keeps returning 429 errors", "technical"),
    ("How do I integrate your SDK with React?", "technical"),
    ("My dashboard is loading really slowly", "technical"),

    # Should route to account
    ("I need to reset my password", "account"),
    ("How do I enable two-factor authentication?", "account"),
    ("Can I change the email on my account?", "account"),

    # Should route to general
    ("What does your product do?", "general"),
    ("What are your business hours?", "general"),
    ("Do you have a mobile app?", "general"),
]


async def main():
    correct = 0
    total = len(test_queries)

    for query, expected in test_queries:
        state = {
            "customer_query": query,
            "messages": [],
            "turn_count": 0,
            "start_time": 0,
            "token_usage": {},
            "retrieved_documents": [],
            "conversation_complete": False,
        }

        result = await agent.process(state)
        routing = result["routing_decision"]
        actual = routing.target_agent
        match = "✓" if actual == expected else "✗"

        if actual == expected:
            correct += 1

        print(f"{match} [{routing.confidence:.2f}] {expected:10} -> {actual:10} | {query[:50]}")

    print(f"\nRouting accuracy: {correct}/{total} ({correct/total:.0%})")
    print(f"Target: 95%+")


if __name__ == "__main__":
    asyncio.run(main())