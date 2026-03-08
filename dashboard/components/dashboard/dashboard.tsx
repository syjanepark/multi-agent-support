'use client'

import { useHealth, useMetrics } from '@/hooks/use-dashboard-data'
import { MetricsCards } from './metrics-cards'
import {
  AgentDistributionChart,
  AgentPerformanceChart,
  LatencyHistogramChart,
  CostOverTimeChart,
} from './charts'
import { QueryTester } from './query-tester'
import { ConnectionStatus } from './connection-status'

export function Dashboard() {
  const { data: health, isLoading: healthLoading } = useHealth(10000)
  const { data: metrics, isLoading: metricsLoading } = useMetrics(30000)

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
          <div>
            <h1 className="text-xl font-semibold tracking-tight">AI Support Dashboard</h1>
            <p className="text-sm text-muted-foreground">Multi-agent customer support monitoring</p>
          </div>
          <ConnectionStatus />
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-7xl space-y-6 px-4 py-6">
        {/* Metrics cards */}
        <section>
          <MetricsCards
            metrics={metrics}
            health={health}
            isLoading={healthLoading || metricsLoading}
          />
        </section>

        {/* Charts row 1 */}
        <section className="grid gap-6 lg:grid-cols-2">
          <AgentDistributionChart metrics={metrics} isLoading={metricsLoading} />
          <AgentPerformanceChart metrics={metrics} isLoading={metricsLoading} />
        </section>

        {/* Charts row 2 */}
        <section className="grid gap-6 lg:grid-cols-2">
          <LatencyHistogramChart metrics={metrics} isLoading={metricsLoading} />
          <CostOverTimeChart metrics={metrics} isLoading={metricsLoading} />
        </section>

        {/* Query tester */}
        <section>
          <QueryTester />
        </section>
      </main>
    </div>
  )
}
