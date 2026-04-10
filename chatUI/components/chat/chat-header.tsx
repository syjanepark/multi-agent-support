'use client'

import { MessageCircle, PanelRightClose, PanelRightOpen, Menu } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ChatHeaderProps {
  sidebarOpen: boolean
  onToggleSidebar: () => void
  onMobileSidebarOpen?: () => void
}

export function ChatHeader({ sidebarOpen, onToggleSidebar, onMobileSidebarOpen }: ChatHeaderProps) {
  return (
    <header className="flex items-center justify-between border-b border-border bg-background px-4 py-3 md:px-6">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary text-primary-foreground">
          <MessageCircle className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-lg font-semibold text-foreground">Customer Support</h1>
          <p className="text-sm text-muted-foreground">Powered by AI - Ask us anything</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={onMobileSidebarOpen}
          className="md:hidden"
          aria-label="Open session info"
        >
          <Menu className="h-5 w-5" />
        </Button>
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleSidebar}
          className="hidden md:flex"
          aria-label={sidebarOpen ? 'Close sidebar' : 'Open sidebar'}
        >
          {sidebarOpen ? (
            <PanelRightClose className="h-5 w-5" />
          ) : (
            <PanelRightOpen className="h-5 w-5" />
          )}
        </Button>
      </div>
    </header>
  )
}
