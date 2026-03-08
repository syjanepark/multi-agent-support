export interface HealthResponse {
  status: string
  version: string
  agents: string[]
  uptime_seconds: number
}

export interface AgentPerformance {
  accuracy: number
  avg_relevance: number
  avg_response_time: number
  total_cases: number
}

export interface CostDataPoint {
  timestamp: string
  cumulative_cost: number
}

export interface MetricsResponse {
  total_queries: number
  avg_response_time: number
  avg_cost: number
  escalation_rate: number
  agent_distribution: Record<string, number>
  agent_performance: Record<string, AgentPerformance>
  latency_histogram: number[]
  cost_over_time: CostDataPoint[]
}

export interface SupportResponse {
  response: string
  agent_used: string
  confidence: number
  routing_confidence: number
  sources: string[]
  suggested_followups: string[]
  was_escalated: boolean
  response_time: number
  cost: number
}
