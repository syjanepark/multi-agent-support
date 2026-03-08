'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { AlertTriangle, Send, Loader2 } from 'lucide-react'
import { submitQuery } from '@/hooks/use-dashboard-data'
import type { SupportResponse } from '@/lib/types'

const AGENT_ICONS: Record<string, string> = {
  billing: '💳',
  technical: '🔧',
  account: '👤',
  general: '💬',
}

function ConfidenceBar({ label, value }: { label: string; value: number }) {
  const percentage = value * 100
  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted-foreground">{label}</span>
        <span className="font-medium">{percentage.toFixed(0)}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full bg-primary transition-all duration-500"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

export function QueryTester() {
  const [query, setQuery] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<SupportResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!query.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      const response = await submitQuery(query)
      setResult(response)
    } catch {
      setError('Failed to process query. Make sure the API is running.')
    } finally {
      setIsLoading(false)
    }
  }

  function handleFollowupClick(followup: string) {
    setQuery(followup)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Live Query Tester</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter a customer query..."
            disabled={isLoading}
            className="flex-1"
          />
          <Button type="submit" disabled={isLoading || !query.trim()}>
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
            <span className="ml-2">Process Query</span>
          </Button>
        </form>

        {error && (
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
            {error}
          </div>
        )}

        {result && (
          <div className="space-y-4 rounded-lg border border-border bg-card/50 p-4">
            {result.was_escalated ? (
              <div className="flex items-center gap-2 rounded-lg bg-warning/20 p-3 text-warning">
                <AlertTriangle className="h-5 w-5" />
                <span className="font-medium">This query was escalated to a human agent</span>
              </div>
            ) : (
              <>
                {/* Agent info */}
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{AGENT_ICONS[result.agent_used] || '🤖'}</span>
                  <div>
                    <p className="font-medium capitalize">{result.agent_used} Agent</p>
                    <div className="flex gap-2">
                      <Badge variant="secondary" className="text-xs">
                        {result.response_time.toFixed(2)}s
                      </Badge>
                      <Badge variant="secondary" className="text-xs">
                        ${result.cost.toFixed(4)}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Confidence bars */}
                <div className="grid gap-3 sm:grid-cols-2">
                  <ConfidenceBar label="Routing Confidence" value={result.routing_confidence} />
                  <ConfidenceBar label="Response Confidence" value={result.confidence} />
                </div>

                {/* Response */}
                <div className="space-y-1">
                  <p className="text-xs text-muted-foreground">Response</p>
                  <p className="text-sm leading-relaxed">{result.response}</p>
                </div>

                {/* Sources */}
                {result.sources && result.sources.length > 0 && (
                  <div className="space-y-1">
                    <p className="text-xs text-muted-foreground">Sources</p>
                    <div className="flex flex-wrap gap-1">
                      {result.sources.map((source, i) => (
                        <Badge key={i} variant="outline" className="text-xs">
                          {source}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {/* Follow-ups */}
                {result.suggested_followups && result.suggested_followups.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-xs text-muted-foreground">Suggested Follow-ups</p>
                    <div className="flex flex-wrap gap-2">
                      {result.suggested_followups.map((followup, i) => (
                        <button
                          key={i}
                          onClick={() => handleFollowupClick(followup)}
                          className="rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-xs text-primary transition-colors hover:bg-primary/20"
                        >
                          {followup}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
