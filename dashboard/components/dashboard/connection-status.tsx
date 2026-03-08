'use client'

import { useHealth } from '@/hooks/use-dashboard-data'

export function ConnectionStatus() {
  const { data, error, isLoading } = useHealth(10000)

  const isConnected = !error && data?.status === 'healthy'

  return (
    <div className="flex items-center gap-2 text-sm">
      <div className="relative flex items-center">
        <span
          className={`h-2.5 w-2.5 rounded-full ${
            isLoading
              ? 'bg-muted-foreground'
              : isConnected
                ? 'bg-green-500'
                : 'bg-red-500'
          }`}
        />
        {isConnected && (
          <span className="absolute h-2.5 w-2.5 animate-ping rounded-full bg-green-500 opacity-75" />
        )}
      </div>
      <span className="text-muted-foreground">
        {isLoading
          ? 'Checking...'
          : isConnected
            ? `Connected (v${data?.version || '?'})`
            : 'Disconnected'}
      </span>
      {data?.uptime_seconds && isConnected && (
        <span className="text-xs text-muted-foreground/60">
          • Uptime: {formatUptime(data.uptime_seconds)}
        </span>
      )}
    </div>
  )
}

function formatUptime(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}
