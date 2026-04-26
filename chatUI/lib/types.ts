export interface SupportResponse {
  response: string
  agent_used: string
  confidence: number
  routing_confidence: number
  sources: string[]
  suggested_followups: string[]
  was_escalated: boolean
  response_time: number
  cost: number
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  agentUsed?: string
  sources?: string[]
  suggestedFollowups?: string[]
  wasEscalated?: boolean
  responseTime?: number
  cost?: number
  isStreaming?: boolean
}

export const AGENT_CONFIG: Record<string, { emoji: string; label: string; colorClass: string }> = {
  billing: { emoji: '💳', label: 'Billing Support', colorClass: 'bg-agent-billing' },
  technical: { emoji: '🔧', label: 'Technical Support', colorClass: 'bg-agent-technical' },
  account: { emoji: '👤', label: 'Account Support', colorClass: 'bg-agent-account' },
  general: { emoji: '💬', label: 'General Support', colorClass: 'bg-agent-general' },
}

export const EXAMPLE_QUESTIONS = [
  { text: 'I was charged twice for my subscription', icon: '💳' },
  { text: 'The API keeps returning 429 errors', icon: '🔧' },
  { text: 'How do I enable two-factor authentication?', icon: '🔐' },
  { text: 'What plans do you offer?', icon: '📋' },
]
