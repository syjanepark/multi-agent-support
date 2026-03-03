import asyncio
import time
from graph.orchestrator import support_graph


test_queries = [
    # Normal routing
    "I was charged twice for my subscription",
    "The API returns 429 errors when I make requests",
    "How do I enable two-factor authentication?",
    "What platforms do you support?",

    # Should escalate
    "I need a refund for $800",
    "I think my account has been hacked",
    "The entire system seems to be down",

    # Edge cases
    "I want to cancel my account and get a refund",  # billing or account?
    "Why is the API slow and how much does the enterprise plan cost?",  # multi-domain
    "hello",  # vague
]


async def main():
    print("=" * 70)
    print("END-TO-END MULTI-AGENT TEST")
    print("=" * 70)

    for query in test_queries:
        start = time.time()

        result = await support_graph.ainvoke(
            {
                "customer_query": query,
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
            config={"configurable": {"thread_id": query[:20]}},
        )

        elapsed = time.time() - start
        routing = result.get("routing_decision")
        agent = result.get("current_agent", "unknown")
        response = result.get("final_response", "No response")

        print(f"\nQuery: {query}")
        print(f"  Agent: {agent} | Confidence: {routing.confidence:.2f}" if routing else "  Agent: escalated")
        print(f"  Time: {elapsed:.2f}s")
        print(f"  Response: {response[:120]}...")
        print("-" * 70)


if __name__ == "__main__":
    asyncio.run(main())