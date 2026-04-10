'use client'

export function TypingIndicator() {
  return (
    <div className="flex items-start gap-3">
      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary">
        <span className="text-sm">🤖</span>
      </div>
      <div className="flex items-center gap-1 rounded-2xl rounded-tl-sm bg-secondary px-4 py-3 shadow-sm">
        <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground/60 [animation-delay:-0.3s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground/60 [animation-delay:-0.15s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground/60" />
      </div>
    </div>
  )
}
