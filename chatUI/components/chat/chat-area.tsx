'use client'

import { useEffect, useRef } from 'react'
import { ScrollArea } from '@/components/ui/scroll-area'
import { ChatMessage } from './chat-message'
import { TypingIndicator } from './typing-indicator'
import { WelcomeState } from './welcome-state'
import type { Message } from '@/lib/types'

interface ChatAreaProps {
  messages: Message[]
  isLoading: boolean
  onFollowupClick: (text: string) => void
  onExampleClick: (text: string) => void
}

export function ChatArea({ messages, isLoading, onFollowupClick, onExampleClick }: ChatAreaProps) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  if (messages.length === 0 && !isLoading) {
    return <WelcomeState onQuestionClick={onExampleClick} />
  }

  return (
    <ScrollArea className="flex-1">
      <div className="mx-auto max-w-3xl space-y-6 p-4 md:p-6">
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} onFollowupClick={onFollowupClick} />
        ))}
        {isLoading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  )
}
