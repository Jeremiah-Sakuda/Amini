import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiFetch } from './client'
import type { AuditReport, AuditReportListResponse } from '../types/report'

export function useReports(params?: { framework?: string; page?: number }) {
  const searchParams = new URLSearchParams()
  if (params?.framework) searchParams.set('framework', params.framework)
  if (params?.page) searchParams.set('page', String(params.page))
  const query = searchParams.toString()

  return useQuery({
    queryKey: ['reports', params],
    queryFn: () =>
      apiFetch<AuditReportListResponse>(`/api/v1/reports${query ? `?${query}` : ''}`),
  })
}

export function useReport(reportId: string) {
  return useQuery({
    queryKey: ['report', reportId],
    queryFn: () => apiFetch<AuditReport>(`/api/v1/reports/${reportId}`),
    enabled: !!reportId,
  })
}

export function useGenerateReport() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: {
      framework: string
      period_start: string
      period_end: string
      agent_ids?: string[]
      title?: string
    }) =>
      apiFetch<AuditReport>('/api/v1/reports', {
        method: 'POST',
        body: JSON.stringify(body),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
    },
  })
}
