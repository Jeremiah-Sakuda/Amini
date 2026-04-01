export interface Incident {
  id: string
  title: string
  status: string
  severity: string
  violation_id: string
  session_id: string
  policy_name: string
  regulation: string | null
  regulation_article: string | null
  decision_chain_snapshot: Record<string, unknown> | null
  affected_data_subjects: Record<string, unknown> | null
  remediation_path: string
  resolution_notes: string
  created_at: string
  updated_at: string
}

export interface IncidentListResponse {
  incidents: Incident[]
  total: number
}
