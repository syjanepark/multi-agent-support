'use client'

import { useState, useCallback, useEffect } from 'react'
import { ChatHeader } from './chat-header'
import { ChatArea } from './chat-area'
import { ChatInput } from './chat-input'
import { ChatSidebar } from './chat-sidebar'
import { Sheet, SheetContent, SheetTitle } from '@/components/ui/sheet'
import { VisuallyHidden } from '@radix-ui/react-visually-hidden'
import type { Message } from '@/lib/types'
import { cn } from '@/lib/utils'

function generateSessionId(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'
const API_KEY = process.env.NEXT_PUBLIC_API_KEY ?? ''

export function SupportChat() {
  const [sessionId, setSessionId] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)

  useEffect(() => {
    setSessionId(generateSessionId())
  }, [])

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading || isStreaming) return

      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: 'user',
        content,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, userMessage])
      setIsLoading(true)

      let assistantMsgId: string | null = null

      try {
        const response = await fetch(`${API_BASE}/support/stream`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(API_KEY && { 'X-Api-Key': API_KEY }),
          },
          body: JSON.stringify({ query: content, session_id: sessionId }),
        })

        if (!response.ok) throw new Error('Failed to get response')

        const reader = response.body!.getReader()
        const decoder = new TextDecoder()

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const lines = decoder.decode(value, { stream: true }).split('\n')
          for (const line of lines) {
            if (!line.startsWith('data: ')) continue
            const data = JSON.parse(line.slice(6))

            if (data.type === 'routing') {
              assistantMsgId = crypto.randomUUID()
              setMessages((prev) => [
                ...prev,
                {
                  id: assistantMsgId!,
                  role: 'assistant',
                  content: '',
                  timestamp: new Date(),
                  agentUsed: data.agent_used,
                  isStreaming: true,
                },
              ])
              setIsLoading(false)
              setIsStreaming(true)
            } else if (data.type === 'token' && assistantMsgId) {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsgId ? { ...m, content: m.content + data.content } : m
                )
              )
            } else if (data.type === 'done' && assistantMsgId) {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsgId
                    ? {
                        ...m,
                        isStreaming: false,
                        sources: data.sources,
                        suggestedFollowups: data.suggested_followups,
                        wasEscalated: data.was_escalated,
                        responseTime: data.response_time,
                        cost: data.cost,
                      }
                    : m
                )
              )
              setIsStreaming(false)
            } else if (data.type === 'error') {
              throw new Error(data.message)
            }
          }
        }
      } catch (err) {
        const errorMessage: Message = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: 'Sorry, something went wrong. Please try again in a moment.',
          timestamp: new Date(),
        }
        setMessages((prev) => {
          const filtered = assistantMsgId ? prev.filter((m) => m.id !== assistantMsgId) : prev
          return [...filtered, errorMessage]
        })
        console.error('Support chat error:', err)
      } finally {
        setIsLoading(false)
        setIsStreaming(false)
      }
    },
    [sessionId, isLoading, isStreaming]
  )

  const handleNewConversation = useCallback(() => {
    setSessionId(generateSessionId())
    setMessages([])
    setMobileSidebarOpen(false)
  }, [])

  return (
    <div className="flex h-screen flex-col bg-background">
      <ChatHeader
        sidebarOpen={sidebarOpen}
        onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        onMobileSidebarOpen={() => setMobileSidebarOpen(true)}
      />

      <div className="flex flex-1 overflow-hidden">
        <main className="flex flex-1 flex-col">
          <ChatArea
            messages={messages}
            isLoading={isLoading}
            onFollowupClick={sendMessage}
            onExampleClick={sendMessage}
          />
          <ChatInput onSend={sendMessage} disabled={isLoading || isStreaming} />
        </main>

        {/* Desktop Sidebar */}
        <div
          className={cn(
            'hidden transition-all duration-300 md:block',
            sidebarOpen ? 'w-80' : 'w-0 overflow-hidden'
          )}
        >
          <ChatSidebar
            sessionId={sessionId}
            messages={messages}
            onNewConversation={handleNewConversation}
            onClose={() => setSidebarOpen(false)}
          />
        </div>
      </div>

      {/* Mobile Sidebar Sheet */}
      <Sheet open={mobileSidebarOpen} onOpenChange={setMobileSidebarOpen}>
        <SheetContent side="right" className="w-80 p-0">
          <VisuallyHidden><SheetTitle>Navigation</SheetTitle></VisuallyHidden>
          <ChatSidebar
            sessionId={sessionId}
            messages={messages}
            onNewConversation={handleNewConversation}
            onClose={() => setMobileSidebarOpen(false)}
          />
        </SheetContent>
      </Sheet>
    </div>
  )
}

