'use client'

import { Card, CardContent } from '@/components/ui/card'
import { Activity, Clock, DollarSign, AlertTriangle, Users } from 'lucide-react'
import type { MetricsResponse, HealthResponse } from '@/lib/types'

interface MetricsCardsProps {
  metrics: MetricsResponse | undefined
  health: HealthResponse | undefined
  isLoading: boolean
}

export function MetricsCards({ metrics, health, isLoading }: MetricsCardsProps) {
  const cards = [
    {
      label: 'Total Queries',
      value: metrics?.total_queries ?? 0,
      format: (v: number) => v.toLocaleString(),
      icon: Activity,
      color: '#3b82f6',
    },
    {
      label: 'Avg Response Time',
      value: metrics?.avg_response_time ?? 0,
      format: (v: number) => `${v.toFixed(2)}s`,
      icon: Clock,
      color: '#22c55e',
    },
    {
      label: 'Avg Cost/Query',
      value: metrics?.avg_cost ?? 0,
      format: (v: number) => `$${v.toFixed(4)}`,
      icon: DollarSign,
      color: '#f59e0b',
    },
    {
      label: 'Escalation Rate',
      value: metrics?.escalation_rate ?? 0,
      format: (v: number) => `${(v * 100).toFixed(1)}%`,
      icon: AlertTriangle,
      color: '#ef4444',
    },
    {
      label: 'Active Agents',
      value: health?.agents?.length ?? 0,
      format: (v: number) => v.toString(),
      icon: Users,
      color: '#8b5cf6',
    },
  ]

  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-5">
      {cards.map((card) => (
        <Card key={card.label} className="relative overflow-hidden">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">{card.label}</p>
                {isLoading ? (
                  <div className="h-8 w-16 animate-pulse rounded bg-muted" />
                ) : (
                  <p className="text-2xl font-bold">{card.format(card.value)}</p>
                )}
              </div>
              <div
                className="rounded-lg p-2"
                style={{ backgroundColor: `${card.color}20` }}
              >
                <card.icon className="h-5 w-5" style={{ color: card.color }} />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
