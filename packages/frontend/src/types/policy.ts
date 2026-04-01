export interface PolicyVersion {
  id: string
  version_number: number
  tier: string
  enforcement: string
  severity: string
  message: string
  scope: Record<string, unknown> | null
  is_active: boolean
  created_at: string
}

export interface Policy {
  id: string
  name: string
  description: string
  is_active: boolean
  latest_version: PolicyVersion | null
  created_at: string
}
