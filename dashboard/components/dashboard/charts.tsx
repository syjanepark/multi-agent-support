'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
  ReferenceLine,
} from 'recharts'
import type { MetricsResponse } from '@/lib/types'

interface ChartsProps {
  metrics: MetricsResponse | undefined
  isLoading: boolean
}

const AGENT_COLORS: Record<string, string> = {
  billing: '#3b82f6',
  technical: '#22c55e',
  account: '#f59e0b',
  general: '#8b5cf6',
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex h-[250px] items-center justify-center text-muted-foreground">
      {message}
    </div>
  )
}

function LoadingState() {
  return (
    <div className="flex h-[250px] items-center justify-center">
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-primary border-t-transparent" />
    </div>
  )
}

export function AgentDistributionChart({ metrics, isLoading }: ChartsProps) {
  if (isLoading) return <Card><CardHeader><CardTitle>Agent Distribution</CardTitle></CardHeader><CardContent><LoadingState /></CardContent></Card>

  const data = metrics?.agent_distribution
    ? Object.entries(metrics.agent_distribution).map(([name, value]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        value,
        fill: AGENT_COLORS[name] || '#94a3b8',
      }))
    : []

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Agent Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <EmptyState message="No data yet" />
        ) : (
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={2}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                labelLine={false}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: '#f8fafc',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  )
}

export function AgentPerformanceChart({ metrics, isLoading }: ChartsProps) {
  if (isLoading) return <Card><CardHeader><CardTitle>Agent Performance</CardTitle></CardHeader><CardContent><LoadingState /></CardContent></Card>

  const data = metrics?.agent_performance
    ? Object.entries(metrics.agent_performance).map(([name, perf]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        accuracy: perf.accuracy * 100,
        responseTime: perf.avg_response_time,
        fill: AGENT_COLORS[name] || '#94a3b8',
      }))
    : []

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Agent Performance</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <EmptyState message="No data yet" />
        ) : (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={data} barGap={4}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis yAxisId="left" tick={{ fill: '#94a3b8', fontSize: 12 }} domain={[0, 100]} />
              <YAxis yAxisId="right" orientation="right" tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: '#f8fafc',
                }}
              />
              <Legend wrapperStyle={{ color: '#94a3b8' }} />
              <Bar yAxisId="left" dataKey="accuracy" name="Accuracy %" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              <Bar yAxisId="right" dataKey="responseTime" name="Resp. Time (s)" fill="#22c55e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  )
}

export function LatencyHistogramChart({ metrics, isLoading }: ChartsProps) {
  if (isLoading) return <Card><CardHeader><CardTitle>Response Time Distribution</CardTitle></CardHeader><CardContent><LoadingState /></CardContent></Card>

  const histogram = metrics?.latency_histogram || []
  const binSize = 0.5
  const bins: Record<string, number> = {}

  histogram.forEach((latency) => {
    const binIndex = Math.floor(latency / binSize)
    const binLabel = `${(binIndex * binSize).toFixed(1)}-${((binIndex + 1) * binSize).toFixed(1)}s`
    bins[binLabel] = (bins[binLabel] || 0) + 1
  })

  const data = Object.entries(bins).map(([range, count]) => ({
    range,
    count,
    midpoint: parseFloat(range.split('-')[0]) + binSize / 2,
  })).sort((a, b) => a.midpoint - b.midpoint)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Response Time Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <EmptyState message="No data yet" />
        ) : (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="range" tick={{ fill: '#94a3b8', fontSize: 10 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: '#f8fafc',
                }}
              />
              <ReferenceLine
                x={data.findIndex(d => d.midpoint >= 2.0) >= 0 ? data.find(d => d.midpoint >= 2.0)?.range : undefined}
                stroke="#ef4444"
                strokeDasharray="5 5"
                strokeWidth={2}
                label={{
                  value: 'SLA Target (2.0s)',
                  position: 'top',
                  fill: '#ef4444',
                  fontSize: 11,
                }}
              />
              <Bar dataKey="count" name="Queries" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  )
}

export function CostOverTimeChart({ metrics, isLoading }: ChartsProps) {
  if (isLoading) return <Card><CardHeader><CardTitle>Cumulative Cost Over Time</CardTitle></CardHeader><CardContent><LoadingState /></CardContent></Card>

  const data = metrics?.cost_over_time?.map((point) => ({
    time: new Date(point.timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    }),
    cost: point.cumulative_cost,
  })) || []

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Cumulative Cost Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <EmptyState message="No data yet" />
        ) : (
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={data}>
              <defs>
                <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="time" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis tick={{ fill: '#94a3b8', fontSize: 12 }} tickFormatter={(v) => `$${v.toFixed(2)}`} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: '#f8fafc',
                }}
                formatter={(value: number) => [`$${value.toFixed(4)}`, 'Cost']}
              />
              <Area
                type="monotone"
                dataKey="cost"
                stroke="#22c55e"
                fill="url(#costGradient)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  )
}
