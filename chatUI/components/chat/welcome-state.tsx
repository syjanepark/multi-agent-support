'use client'

import { MessageCircle, Sparkles } from 'lucide-react'
import { EXAMPLE_QUESTIONS } from '@/lib/types'

interface WelcomeStateProps {
  onQuestionClick: (question: string) => void
}

export function WelcomeState({ onQuestionClick }: WelcomeStateProps) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center px-4 py-8">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 text-primary">
        <MessageCircle className="h-8 w-8" />
      </div>
      <h2 className="mt-6 text-center text-2xl font-semibold text-foreground">
        How can we help you today?
      </h2>
      <p className="mt-2 max-w-md text-center text-muted-foreground">
        Ask us anything about your account, billing, technical issues, or general questions. Our AI-powered support is here 24/7.
      </p>

      <div className="mt-8 grid w-full max-w-lg gap-3 md:grid-cols-2">
        {EXAMPLE_QUESTIONS.map((q, idx) => (
          <button
            key={idx}
            onClick={() => onQuestionClick(q.text)}
            className="group flex items-start gap-3 rounded-xl border border-border bg-background p-4 text-left transition-all hover:border-primary/50 hover:bg-primary/5 hover:shadow-md"
          >
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-secondary text-lg transition-colors group-hover:bg-primary/10">
              {q.icon}
            </span>
            <span className="text-sm text-foreground leading-relaxed">{q.text}</span>
          </button>
        ))}
      </div>

      <div className="mt-8 flex items-center gap-2 text-sm text-muted-foreground">
        <Sparkles className="h-4 w-4" />
        <span>Powered by multi-agent AI</span>
      </div>
    </div>
  )
}
