'use client'

import useSWR from 'swr'
import type { HealthResponse, MetricsResponse, SupportResponse } from '@/lib/types'

const API_BASE = 'http://localhost:8000'

const fetcher = async (url: string) => {
  const res = await fetch(url)
  if (!res.ok) throw new Error('Failed to fetch')
  return res.json()
}

export function useHealth(refreshInterval = 10000) {
  return useSWR<HealthResponse>(
    `${API_BASE}/health`,
    fetcher,
    {
      refreshInterval,
      revalidateOnFocus: false,
      shouldRetryOnError: false,
    }
  )
}

export function useMetrics(refreshInterval = 30000) {
  return useSWR<MetricsResponse>(
    `${API_BASE}/metrics`,
    fetcher,
    {
      refreshInterval,
      revalidateOnFocus: false,
      shouldRetryOnError: false,
    }
  )
}

export async function submitQuery(query: string): Promise<SupportResponse> {
  const res = await fetch(`${API_BASE}/support`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query }),
  })
  if (!res.ok) throw new Error('Failed to submit query')
  return res.json()
}
