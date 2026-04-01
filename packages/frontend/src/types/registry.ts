export interface AgentRegistryEntry {
  id: string
  agent_external_id: string
  name: string
  description: string | null
  framework: string
  provider: string
  risk_class: string
  tags: string[] | null
  data_access_patterns: Record<string, unknown> | null
  deployment_status: string
  discovery_method: string
  regulations: string[] | null
  session_count: number
  violation_count: number
  created_at: string
  updated_at: string
}

export interface AgentRegistryListResponse {
  agents: AgentRegistryEntry[]
  total: number
}
