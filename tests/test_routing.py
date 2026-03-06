"""Run suspected misrouted queries through the triage agent only to diagnose routing failures."""
import asyncio
from agents.triage_agent import TriageAgent
from graph.state import GraphState


CANDIDATES = [
    # Verify fixes for the 4 misrouted queries
    {"id": "billing_002", "query": "What's the difference between the Starter and Professional plans?", "expected": "billing"},
    {"id": "billing_010", "query": "We have a team of 50 engineers. Can we get volume pricing or negotiate an enterprise contract?", "expected": "billing"},
    {"id": "technical_013", "query": "What's the best approach to process thousands of documents through the API without hitting rate limits?", "expected": "technical"},
    {"id": "general_012", "query": "What models do you offer and what are their context window sizes? Also, how do I authenticate my first API request?", "expected": "general"},
    # Verify vague-query escalation fix
    {"id": "general_004", "query": "help", "expected": "general"},
    {"id": "general_008", "query": "I have a problem", "expected": "general"},
]


async def main():
    agent = TriageAgent()
    print(f"\n{'ID':<16} {'Expected':<12} {'Got':<12} {'Conf':>6}  {'OK?':>4}  Reasoning")
    print("-" * 90)

    for c in CANDIDATES:
        state: GraphState = {
            "customer_query": c["query"],
            "messages": [],
            "turn_count": 0,
            "start_time": 0,
            "token_usage": {},
            "retrieved_documents": [],
            "conversation_complete": False,
            "customer_context": None,
            "routing_decision": None,
            "current_agent": None,
            "agent_response": None,
            "error": None,
            "final_response": None,
        }
        result = await agent.process(state)
        routing = result["routing_decision"]
        ok = "✓" if routing.target_agent == c["expected"] else "✗"
        print(f"{c['id']:<16} {c['expected']:<12} {routing.target_agent:<12} {routing.confidence:>6.2f}  {ok:>4}  {routing.reasoning}")


if __name__ == "__main__":
    asyncio.run(main())
