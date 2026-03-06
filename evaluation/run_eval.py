import asyncio
from evaluation.evaluator import SystemEvaluator


async def main():
    evaluator = SystemEvaluator()
    await evaluator.evaluate_dataset("evaluation/ground_truth.json")


if __name__ == "__main__":
    asyncio.run(main())