export interface Violation {
  id: string
  session_id: string
  decision_node_id: string | null
  policy_version_id: string
  severity: string
  violation_type: string
  description: string
  evidence: Record<string, unknown> | null
  created_at: string
}

export interface ViolationListResponse {
  violations: Violation[]
  total: number
  page: number
  page_size: number
}
