export interface AuditReport {
  id: string
  title: string
  report_type: string
  framework: string
  status: string
  period_start: string
  period_end: string
  agent_ids: string[] | null
  summary: string
  gap_analysis: Record<string, unknown> | null
  content: Record<string, unknown> | null
  created_at: string
}

export interface AuditReportListResponse {
  reports: AuditReport[]
  total: number
}
