'use client'

import { Clock, DollarSign, Hash, MessageSquare, RefreshCcw, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import type { Message } from '@/lib/types'

interface ChatSidebarProps {
  sessionId: string
  messages: Message[]
  onNewConversation: () => void
  onClose: () => void
}

export function ChatSidebar({ sessionId, messages, onNewConversation, onClose }: ChatSidebarProps) {
  const assistantMessages = messages.filter((m) => m.role === 'assistant')
  const totalCost = assistantMessages.reduce((sum, m) => sum + (m.cost || 0), 0)

  return (
    <aside className="flex h-full w-80 flex-col border-l border-border bg-sidebar">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-sidebar-border px-4 py-3">
        <h2 className="font-semibold text-sidebar-foreground">Session Info</h2>
        <Button variant="ghost" size="icon-sm" onClick={onClose} className="md:hidden">
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* Session Details */}
      <div className="flex-1 overflow-y-auto p-4">
        {/* Session ID */}
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Hash className="h-4 w-4" />
            <span>Session ID</span>
          </div>
          <p className="rounded-md bg-sidebar-accent px-3 py-2 font-mono text-xs text-sidebar-foreground">
            {sessionId.slice(0, 8)}...{sessionId.slice(-4)}
          </p>
        </div>

        {/* Message Count */}
        <div className="mt-4 space-y-1">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <MessageSquare className="h-4 w-4" />
            <span>Messages</span>
          </div>
          <p className="text-2xl font-semibold text-sidebar-foreground">{messages.length}</p>
        </div>

        {/* Total Cost */}
        <div className="mt-4 space-y-1">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <DollarSign className="h-4 w-4" />
            <span>Total Session Cost</span>
          </div>
          <p className="text-2xl font-semibold text-sidebar-foreground">${totalCost.toFixed(4)}</p>
        </div>

        <Separator className="my-6" />

        {/* Per-message metrics */}
        <div className="space-y-2">
          <h3 className="text-sm font-medium text-sidebar-foreground">Message Metrics</h3>
          {assistantMessages.length === 0 ? (
            <p className="text-sm text-muted-foreground">No messages yet</p>
          ) : (
            <div className="space-y-2">
              {assistantMessages.map((msg, idx) => (
                <div
                  key={msg.id}
                  className="rounded-lg border border-sidebar-border bg-sidebar-accent/50 p-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-sidebar-foreground">
                      Response {idx + 1}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {msg.agentUsed || 'General'}
                    </span>
                  </div>
                  <div className="mt-2 flex items-center gap-4 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {msg.responseTime?.toFixed(0) || '—'}ms
                    </span>
                    <span className="flex items-center gap-1">
                      <DollarSign className="h-3 w-3" />
                      ${msg.cost?.toFixed(4) || '0.0000'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="border-t border-sidebar-border p-4">
        <Button onClick={onNewConversation} variant="outline" className="w-full gap-2">
          <RefreshCcw className="h-4 w-4" />
          New Conversation
        </Button>
      </div>
    </aside>
  )
}
