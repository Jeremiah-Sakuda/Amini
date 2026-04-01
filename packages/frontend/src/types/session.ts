import type { DecisionNode } from './decision'
import type { Violation } from './violation'

export interface Session {
  id: string
  session_external_id: string
  agent_id: string
  environment: string
  status: string
  user_context: Record<string, unknown> | null
  violation_count: number
  decision_count: number
  created_at: string
  updated_at: string
}

export interface SessionDetail {
  id: string
  session_external_id: string
  agent_id: string
  environment: string
  status: string
  user_context: Record<string, unknown> | null
  audit_metadata: Record<string, unknown> | null
  terminal_reason: string | null
  decisions: DecisionNode[]
  violations: Violation[]
  created_at: string
  updated_at: string
}

export interface SessionListResponse {
  sessions: Session[]
  total: number
  page: number
  page_size: number
}
