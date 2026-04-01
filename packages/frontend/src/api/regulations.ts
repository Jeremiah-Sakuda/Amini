import { useQuery } from '@tanstack/react-query'
import { apiFetch } from './client'
import type { RegulationListResponse, ComplianceOverviewResponse } from '../types/regulation'

export function useRegulations() {
  return useQuery({
    queryKey: ['regulations'],
    queryFn: () => apiFetch<RegulationListResponse>('/api/v1/regulations'),
  })
}

export function useComplianceOverview(agentId: string) {
  return useQuery({
    queryKey: ['compliance', agentId],
    queryFn: () =>
      apiFetch<ComplianceOverviewResponse>(`/api/v1/regulations/compliance/${agentId}`),
    enabled: !!agentId,
  })
}
