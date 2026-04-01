export interface RegulatoryRequirement {
  id: string
  article: string
  section: string
  title: string
  description: string
  evidence_types: Record<string, unknown> | null
  applies_to_risk_class: string | null
  review_cadence_days: number
}

export interface Regulation {
  id: string
  name: string
  short_code: string
  version: string
  jurisdiction: string
  description: string
  effective_date: string | null
  is_active: boolean
  requirements: RegulatoryRequirement[]
  created_at: string
}

export interface RegulationListResponse {
  regulations: Regulation[]
  total: number
}

export interface ComplianceMappingResponse {
  id: string
  agent_id: string
  requirement_id: string
  requirement_article: string
  requirement_title: string
  regulation_name: string
  status: string
  evidence: Record<string, unknown> | null
  notes: string
  last_reviewed: string | null
  next_review_due: string | null
}

export interface ComplianceGapResponse {
  regulation: string
  total_requirements: number
  assessed: number
  compliant: number
  non_compliant: number
  partially_compliant: number
  not_assessed: number
  compliance_percentage: number
  gaps: ComplianceMappingResponse[]
}

export interface ComplianceOverviewResponse {
  agent_id: string
  agent_name: string
  regulations: ComplianceGapResponse[]
}
