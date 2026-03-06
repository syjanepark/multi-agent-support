import asyncio
import time
from graph.orchestrator import support_graph


async def main():
    query = "The API keeps returning 429 errors when I make requests"
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
        config={"configurable": {"thread_id": "debug-1"}},
    )

    elapsed = time.time() - start
    print(f"\nQuery: {query}")
    print(f"Agent: {result.get('current_agent')}")
    print(f"Time: {elapsed:.2f}s")
    print(f"Response: {result.get('final_response', 'None')[:200]}")


if __name__ == "__main__":
    asyncio.run(main())