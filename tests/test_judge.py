import asyncio
from evaluation.evaluator import SystemEvaluator


async def main():
    evaluator = SystemEvaluator()

    test_cases = [
        {
            "query": "What plans do you offer?",
            "response": "We offer Starter ($29/mo), Professional ($99/mo), and Enterprise ($299/mo). Each includes different API call limits and support levels.",
            "topics": ["pricing", "plans", "features"],
        },
        {
            "query": "What plans do you offer?",
            "response": "I like pizza.",
            "topics": ["pricing", "plans", "features"],
        },
    ]

    for case in test_cases:
        score = await evaluator._judge_relevance(
            case["query"], case["response"], case["topics"]
        )
        print(f"Score: {score} | Response: {case['response'][:50]}")


if __name__ == "__main__":
    asyncio.run(main())