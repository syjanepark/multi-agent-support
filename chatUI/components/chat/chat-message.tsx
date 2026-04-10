'use client'

import { ExternalLink } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import type { Message } from '@/lib/types'
import { AGENT_CONFIG } from '@/lib/types'

interface ChatMessageProps {
  message: Message
  onFollowupClick: (text: string) => void
}

export function ChatMessage({ message, onFollowupClick }: ChatMessageProps) {
  const isUser = message.role === 'user'

  const agentConfig = message.agentUsed
    ? AGENT_CONFIG[message.agentUsed.toLowerCase()] || AGENT_CONFIG.general
    : null

  return (
    <div
      className={cn(
        'flex animate-in fade-in-0 slide-in-from-bottom-2 duration-300',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      <div className={cn('flex max-w-[85%] flex-col gap-1', isUser ? 'items-end' : 'items-start')}>
        {/* Agent Badge */}
        {!isUser && agentConfig && (
          <Badge
            variant="secondary"
            className={cn(
              'mb-1 text-xs font-medium text-foreground',
              message.wasEscalated ? 'bg-agent-escalated/20' : `${agentConfig.colorClass}/20`
            )}
          >
            <span className="mr-1">{message.wasEscalated ? '⚠️' : agentConfig.emoji}</span>
            {message.wasEscalated ? 'Escalating to Human' : agentConfig.label}
          </Badge>
        )}

        {/* Message Bubble */}
        <div
          className={cn(
            'rounded-2xl px-4 py-2.5 shadow-sm',
            isUser
              ? 'rounded-tr-sm bg-primary text-primary-foreground'
              : message.wasEscalated
                ? 'rounded-tl-sm border-2 border-agent-escalated/30 bg-agent-escalated/10 text-foreground'
                : 'rounded-tl-sm bg-secondary text-foreground'
          )}
        >
          <div className="prose prose-sm max-w-none dark:prose-invert">
            {renderMarkdown(message.content)}
          </div>
        </div>

        {/* Sources */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-1 flex flex-wrap gap-1.5">
            {message.sources.map((source, idx) => (
              <a
                key={idx}
                href={source}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 rounded-md bg-secondary/80 px-2 py-1 text-xs text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
              >
                <ExternalLink className="h-3 w-3" />
                Source {idx + 1}
              </a>
            ))}
          </div>
        )}

        {/* Suggested Followups */}
        {message.suggestedFollowups && message.suggestedFollowups.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {message.suggestedFollowups.map((followup, idx) => (
              <button
                key={idx}
                onClick={() => onFollowupClick(followup)}
                className="rounded-full border border-border bg-background px-3 py-1.5 text-sm text-foreground transition-all hover:border-primary hover:bg-primary/5"
              >
                {followup}
              </button>
            ))}
          </div>
        )}

        {/* Escalation Message */}
        {message.wasEscalated && (
          <p className="mt-1 text-xs text-agent-escalated">
            Connecting you to a human specialist...
          </p>
        )}
      </div>
    </div>
  )
}

function renderMarkdown(content: string): React.ReactNode {
  // Simple markdown rendering for bold, lists, and code blocks
  const lines = content.split('\n')
  const elements: React.ReactNode[] = []
  let inCodeBlock = false
  let codeContent: string[] = []

  lines.forEach((line, idx) => {
    if (line.startsWith('```')) {
      if (inCodeBlock) {
        elements.push(
          <pre key={`code-${idx}`} className="my-2 overflow-x-auto rounded-lg bg-foreground/5 p-3 font-mono text-sm">
            <code>{codeContent.join('\n')}</code>
          </pre>
        )
        codeContent = []
        inCodeBlock = false
      } else {
        inCodeBlock = true
      }
      return
    }

    if (inCodeBlock) {
      codeContent.push(line)
      return
    }

    // Handle bullet points
    if (line.startsWith('- ') || line.startsWith('* ')) {
      elements.push(
        <div key={idx} className="ml-4 flex items-start gap-2">
          <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-muted-foreground/40" />
          <span>{renderInlineMarkdown(line.slice(2))}</span>
        </div>
      )
      return
    }

    // Handle numbered lists
    const numberedMatch = line.match(/^(\d+)\.\s/)
    if (numberedMatch) {
      elements.push(
        <div key={idx} className="ml-4 flex items-start gap-2">
          <span className="shrink-0 text-muted-foreground">{numberedMatch[1]}.</span>
          <span>{renderInlineMarkdown(line.slice(numberedMatch[0].length))}</span>
        </div>
      )
      return
    }

    // Regular paragraph
    if (line.trim()) {
      elements.push(
        <p key={idx} className="leading-relaxed">
          {renderInlineMarkdown(line)}
        </p>
      )
    } else if (idx > 0 && idx < lines.length - 1) {
      elements.push(<br key={idx} />)
    }
  })

  return <div className="space-y-1">{elements}</div>
}

function renderInlineMarkdown(text: string): React.ReactNode {
  // Handle **bold** and `code`
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g)
  return parts.map((part, idx) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={idx}>{part.slice(2, -2)}</strong>
    }
    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={idx} className="rounded bg-foreground/5 px-1.5 py-0.5 font-mono text-sm">
          {part.slice(1, -1)}
        </code>
      )
    }
    return part
  })
}
