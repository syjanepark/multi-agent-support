import json
import asyncio
import time
from dataclasses import dataclass, field
from openai import AzureOpenAI
from graph.orchestrator import support_graph
from config.settings import get_settings
import structlog

logger = structlog.get_logger()


@dataclass
class EvaluationResult:
    total_cases: int = 0
    routing_correct: int = 0
    routing_accuracy: float = 0.0
    avg_confidence: float = 0.0
    avg_response_time: float = 0.0
    avg_relevance_score: float = 0.0
    total_cost: float = 0.0
    escalation_count: int = 0
    errors: list = field(default_factory=list)
    per_agent_metrics: dict = field(default_factory=dict)


class SystemEvaluator:
    def __init__(self):
        settings = get_settings()
        from openai import AsyncAzureOpenAI
        self.judge = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
        )
        self.judge_model = settings.azure_openai_chat_deployment

    async def evaluate_dataset(self, dataset_path: str) -> EvaluationResult:
        with open(dataset_path) as f:
            cases = json.load(f)

        result = EvaluationResult(total_cases=len(cases))
        semaphore = asyncio.Semaphore(5)

        async def run_with_semaphore(case: dict) -> dict:
            async with semaphore:
                return await self._run_single(case)

        outcomes = await asyncio.gather(
            *[run_with_semaphore(c) for c in cases],
            return_exceptions=True,
        )

        per_agent: dict[str, dict] = {}

        for case, outcome in zip(cases, outcomes):
            if isinstance(outcome, Exception):
                result.errors.append({"id": case["id"], "error": str(outcome)})
                logger.error("case_failed", id=case["id"], error=str(outcome))
                continue

            agent = case["expected_agent"]
            if agent not in per_agent:
                per_agent[agent] = {
                    "correct": 0,
                    "total": 0,
                    "confidences": [],
                    "times": [],
                    "relevances": [],
                    "cost": 0.0,
                }

            per_agent[agent]["total"] += 1

            if outcome["routing_correct"]:
                result.routing_correct += 1
                per_agent[agent]["correct"] += 1

            if outcome["confidence"] is not None:
                per_agent[agent]["confidences"].append(outcome["confidence"])

            per_agent[agent]["times"].append(outcome["response_time"])
            per_agent[agent]["relevances"].append(outcome["relevance_score"])
            per_agent[agent]["cost"] += outcome["cost"]
            result.total_cost += outcome["cost"]

            if outcome["escalated"]:
                result.escalation_count += 1

        # Aggregate across all cases
        all_confidences = [v for m in per_agent.values() for v in m["confidences"]]
        all_times = [v for m in per_agent.values() for v in m["times"]]
        all_relevances = [v for m in per_agent.values() for v in m["relevances"]]

        completed = result.total_cases - len(result.errors)
        result.routing_accuracy = result.routing_correct / completed if completed else 0.0
        result.avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        result.avg_response_time = sum(all_times) / len(all_times) if all_times else 0.0
        result.avg_relevance_score = sum(all_relevances) / len(all_relevances) if all_relevances else 0.0

        for agent, m in per_agent.items():
            result.per_agent_metrics[agent] = {
                "routing_accuracy": m["correct"] / m["total"] if m["total"] else 0.0,
                "correct": m["correct"],
                "total": m["total"],
                "avg_confidence": sum(m["confidences"]) / len(m["confidences"]) if m["confidences"] else 0.0,
                "avg_response_time": sum(m["times"]) / len(m["times"]) if m["times"] else 0.0,
                "avg_relevance_score": sum(m["relevances"]) / len(m["relevances"]) if m["relevances"] else 0.0,
                "total_cost": m["cost"],
            }

        self._print_report(result)
        return result

    async def _run_single(self, case: dict) -> dict:
        start = time.time()

        graph_result = await support_graph.ainvoke(
            {
                "customer_query": case["query"],
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
            config={"configurable": {"thread_id": case["id"]}},
        )

        elapsed = time.time() - start

        routing = graph_result.get("routing_decision")
        agent_response = graph_result.get("agent_response")
        final_response = graph_result.get("final_response") or ""

        actual_agent = routing.target_agent if routing else None
        routing_correct = actual_agent == case["expected_agent"]

        confidence = agent_response.confidence if agent_response else None

        escalated = bool(
            (routing and routing.requires_escalation)
            or (agent_response and agent_response.requires_human)
        )

        token_usage = graph_result.get("token_usage") or {}
        cost = token_usage.get("cost", 0.0)

        relevance_score = await self._judge_relevance(
            case["query"],
            final_response,
            case.get("required_topics", []),
        )

        logger.info(
            "case_evaluated",
            id=case["id"],
            routing_correct=routing_correct,
            actual_agent=actual_agent,
            expected_agent=case["expected_agent"],
            confidence=confidence,
            relevance=relevance_score,
            elapsed=round(elapsed, 2),
        )

        return {
            "routing_correct": routing_correct,
            "actual_agent": actual_agent,
            "confidence": confidence,
            "response_time": elapsed,
            "relevance_score": relevance_score,
            "cost": cost,
            "escalated": escalated,
        }

    async def _judge_relevance(self, query: str, response: str, required_topics: list[str]) -> float:

        if not response:
            return 0.0

        topics_str = ", ".join(required_topics) if required_topics else "none specified"

        prompt = f"""You are evaluating a customer support response. Score it on a scale of 1 to 5.

Customer query: {query}

Support response: {response}

Required topics to cover: {topics_str}

Scoring rubric:
1 = Does not address the query
2 = Partially addresses the query; misses most required topics
3 = Adequately addresses the query; covers some required topics
4 = Addresses the query well; covers most required topics
5 = Fully addresses the query; covers all required topics; professional and helpful

Reply with a single integer (1, 2, 3, 4, or 5) and nothing else."""

        completion = await self.judge.chat.completions.create(
            model=self.judge_model,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=500,
        )

        raw = completion.choices[0].message.content.strip()
        print(f"  Judge raw: '{raw}' | len: {len(raw)}")
        logger.debug("judge_raw_response", raw=raw)
        try:
            score = int(raw[0])
            score = max(1, min(5, score))
        except (ValueError, IndexError):
            logger.warning("judge_parse_failed", raw=raw)
            score = 3

        return score / 5.0  # 1=0.2, 2=0.4, 3=0.6, 4=0.8, 5=1.0

    def _print_report(self, result: EvaluationResult):
        completed = result.total_cases - len(result.errors)
        escalation_rate = result.escalation_count / completed if completed else 0.0

        print("\n" + "=" * 64)
        print("EVALUATION REPORT")
        print("=" * 64)
        print(f"  Cases run:         {completed}/{result.total_cases}")
        print(f"  Routing accuracy:  {result.routing_accuracy:.1%}  ({result.routing_correct}/{completed})")
        print(f"  Avg confidence:    {result.avg_confidence:.3f}")
        print(f"  Avg response time: {result.avg_response_time:.2f}s")
        print(f"  Avg relevance:     {result.avg_relevance_score:.3f}  (0.0–1.0)")
        print(f"  Total cost:        ${result.total_cost:.4f}")
        print(f"  Escalations:       {result.escalation_count}  ({escalation_rate:.1%})")

        if result.per_agent_metrics:
            print("\n  Per-agent breakdown:")
            col = f"  {'Agent':<12}  {'Acc':>6}  {'Crct/Tot':>8}  {'Conf':>6}  {'Time':>7}  {'Rel':>6}  {'Cost':>8}"
            print(col)
            print("  " + "-" * (len(col) - 2))
            for agent, m in sorted(result.per_agent_metrics.items()):
                print(
                    f"  {agent:<12}  {m['routing_accuracy']:>6.1%}  "
                    f"{m['correct']:>4}/{m['total']:<3}  "
                    f"{m['avg_confidence']:>6.3f}  "
                    f"{m['avg_response_time']:>6.2f}s  "
                    f"{m['avg_relevance_score']:>6.3f}  "
                    f"${m['total_cost']:>7.4f}"
                )

        if result.errors:
            print(f"\n  Errors ({len(result.errors)}):")
            for e in result.errors:
                print(f"    {e['id']}: {e['error']}")

        print("=" * 64 + "\n")


if __name__ == "__main__":
    import sys

    dataset = sys.argv[1] if len(sys.argv) > 1 else "evaluation/ground_truth.json"
    evaluator = SystemEvaluator()
    asyncio.run(evaluator.evaluate_dataset(dataset))
