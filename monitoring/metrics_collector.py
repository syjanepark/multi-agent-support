import threading
from datetime import datetime


class MetricsCollector:
    def __init__(self):
        self._lock = threading.Lock()
        self._requests = []

    def record_request(self, request_id: str, agent_used: str,
                       routing_confidence: float, response_confidence: float,
                       response_time: float, cost: float, escalated: bool):
        with self._lock:
            self._requests.append({
                "request_id": request_id,
                "agent_used": agent_used,
                "routing_confidence": routing_confidence,
                "response_confidence": response_confidence,
                "response_time": response_time,
                "cost": cost,
                "escalated": escalated,
                "timestamp": datetime.utcnow().isoformat(),
            })

    def get_summary(self) -> dict:
        with self._lock:
            total = len(self._requests)
            if total == 0:
                return {
                    "total_queries": 0,
                    "avg_response_time": 0.0,
                    "avg_cost": 0.0,
                    "escalation_rate": 0.0,
                    "agent_distribution": {},
                    "agent_performance": {},
                    "latency_histogram": [],
                    "cost_over_time": [],
                }

            agent_dist = {}
            agent_perf = {}
            escalations = 0
            total_time = 0.0
            total_cost = 0.0
            latencies = []
            cost_over_time = []
            cumulative_cost = 0.0

            for r in self._requests:
                agent = r["agent_used"]
                agent_dist[agent] = agent_dist.get(agent, 0) + 1

                if agent not in agent_perf:
                    agent_perf[agent] = {
                        "count": 0,
                        "total_confidence": 0.0,
                        "total_time": 0.0,
                    }
                agent_perf[agent]["count"] += 1
                agent_perf[agent]["total_confidence"] += r["response_confidence"]
                agent_perf[agent]["total_time"] += r["response_time"]

                if r["escalated"]:
                    escalations += 1

                total_time += r["response_time"]
                total_cost += r["cost"]
                latencies.append(r["response_time"])

                cumulative_cost += r["cost"]
                cost_over_time.append({
                    "timestamp": r["timestamp"],
                    "cumulative_cost": round(cumulative_cost, 6),
                })

            agent_performance = {}
            for agent, perf in agent_perf.items():
                n = perf["count"]
                agent_performance[agent] = {
                    "accuracy": perf["total_confidence"] / n,
                    "avg_relevance": perf["total_confidence"] / n,
                    "avg_response_time": perf["total_time"] / n,
                    "total_cases": n,
                }

            return {
                "total_queries": total,
                "avg_response_time": round(total_time / total, 3),
                "avg_cost": round(total_cost / total, 6),
                "escalation_rate": round(escalations / total, 3),
                "agent_distribution": agent_dist,
                "agent_performance": agent_performance,
                "latency_histogram": latencies,
                "cost_over_time": cost_over_time,
            }