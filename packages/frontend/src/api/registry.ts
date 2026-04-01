import { useQuery } from '@tanstack/react-query'
import { apiFetch } from './client'
import type { AgentRegistryListResponse } from '../types/registry'

export function useAgentRegistry(params?: {
  framework?: string
  risk_class?: string
  deployment_status?: string
}) {
  const searchParams = new URLSearchParams()
  if (params?.framework) searchParams.set('framework', params.framework)
  if (params?.risk_class) searchParams.set('risk_class', params.risk_class)
  if (params?.deployment_status) searchParams.set('deployment_status', params.deployment_status)
  const query = searchParams.toString()

  return useQuery({
    queryKey: ['registry', params],
    queryFn: () =>
      apiFetch<AgentRegistryListResponse>(`/api/v1/registry${query ? `?${query}` : ''}`),
  })
}
