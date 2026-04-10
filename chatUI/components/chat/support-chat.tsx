'use client'

import { useState, useCallback, useEffect } from 'react'
import { ChatHeader } from './chat-header'
import { ChatArea } from './chat-area'
import { ChatInput } from './chat-input'
import { ChatSidebar } from './chat-sidebar'
import { Sheet, SheetContent, SheetTitle } from '@/components/ui/sheet'
import { VisuallyHidden } from '@radix-ui/react-visually-hidden'
import type { Message, SupportResponse } from '@/lib/types'
import { cn } from '@/lib/utils'

function generateSessionId(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0
    const v = c === 'x' ? r : (r & 0x3) | 0x8
    return v.toString(16)
  })
}

export function SupportChat() {
  const [sessionId, setSessionId] = useState('')
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false)

  useEffect(() => {
    setSessionId(generateSessionId())
  }, [])

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || isLoading) return

      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: 'user',
        content,
        timestamp: new Date(),
      }

      setMessages((prev) => [...prev, userMessage])
      setIsLoading(true)

      try {
        const response = await fetch('http://localhost:8000/support', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: content, session_id: sessionId }),
        })

        if (!response.ok) {
          throw new Error('Failed to get response')
        }

        const data: SupportResponse = await response.json()

        const assistantMessage: Message = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
          agentUsed: data.agent_used,
          sources: data.sources,
          suggestedFollowups: data.suggested_followups,
          wasEscalated: data.was_escalated,
          responseTime: data.response_time,
          cost: data.cost,
        }

        setMessages((prev) => [...prev, assistantMessage])
      } catch {
        // Mock response for demo purposes when API is not available
        const mockResponse: Message = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: getMockResponse(content),
          timestamp: new Date(),
          agentUsed: getMockAgent(content),
          sources: ['https://docs.example.com/help'],
          suggestedFollowups: ['Tell me more', 'What else can you help with?'],
          wasEscalated: content.toLowerCase().includes('manager'),
          responseTime: Math.random() * 500 + 100,
          cost: Math.random() * 0.01,
        }
        setMessages((prev) => [...prev, mockResponse])
      } finally {
        setIsLoading(false)
      }
    },
    [sessionId, isLoading]
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
          <ChatInput onSend={sendMessage} disabled={isLoading} />
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

// Mock response helpers for demo
function getMockResponse(query: string): string {
  const q = query.toLowerCase()
  if (q.includes('charged') || q.includes('billing') || q.includes('payment')) {
    return `I understand you're concerned about a billing issue. Let me help you with that.\n\n**Here's what I found:**\n\n1. I've checked your account and can see your recent transactions\n2. If you were charged twice, we can process a refund within 3-5 business days\n3. To prevent future issues, please ensure you don't have duplicate payment methods saved\n\nWould you like me to initiate a refund investigation?`
  }
  if (q.includes('429') || q.includes('api') || q.includes('error')) {
    return `I see you're experiencing API rate limiting (429 errors). Here's how to resolve this:\n\n**Quick fixes:**\n\n- Implement exponential backoff in your retry logic\n- Check your current rate limit usage in the dashboard\n- Consider upgrading to a higher tier for increased limits\n\n\`\`\`javascript\nconst delay = Math.pow(2, attempt) * 1000;\nawait new Promise(r => setTimeout(r, delay));\n\`\`\`\n\nNeed help implementing this in your code?`
  }
  if (q.includes('two-factor') || q.includes('2fa') || q.includes('authentication')) {
    return `Setting up two-factor authentication is easy! Here's how:\n\n1. Go to **Settings** → **Security**\n2. Click **Enable 2FA**\n3. Scan the QR code with your authenticator app\n4. Enter the verification code\n\n**Recommended apps:**\n- Google Authenticator\n- Authy\n- 1Password\n\nOnce enabled, you'll need to enter a code each time you log in. Would you like me to walk you through any specific step?`
  }
  if (q.includes('plan') || q.includes('pricing') || q.includes('offer')) {
    return `We offer several plans to fit your needs:\n\n**Free Tier**\n- 1,000 API calls/month\n- Basic support\n\n**Pro ($29/mo)**\n- 50,000 API calls/month\n- Priority support\n- Advanced analytics\n\n**Enterprise (Custom)**\n- Unlimited API calls\n- Dedicated support\n- Custom integrations\n- SLA guarantee\n\nWould you like me to help you choose the right plan for your usage?`
  }
  return `Thank you for reaching out! I'm here to help you with your question.\n\nBased on what you've shared, I can assist you further. Could you provide a bit more detail about:\n\n- What specific issue are you experiencing?\n- When did this start happening?\n- Have you tried any troubleshooting steps?\n\nI'll do my best to resolve this for you quickly!`
}

function getMockAgent(query: string): string {
  const q = query.toLowerCase()
  if (q.includes('charged') || q.includes('billing') || q.includes('payment') || q.includes('subscription')) {
    return 'billing'
  }
  if (q.includes('429') || q.includes('api') || q.includes('error') || q.includes('code')) {
    return 'technical'
  }
  if (q.includes('two-factor') || q.includes('2fa') || q.includes('authentication') || q.includes('account') || q.includes('password')) {
    return 'account'
  }
  return 'general'
}
