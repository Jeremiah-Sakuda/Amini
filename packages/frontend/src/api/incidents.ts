import { useQuery } from '@tanstack/react-query'
import { apiFetch } from './client'
import type { IncidentListResponse } from '../types/incident'

export function useIncidents(params?: {
  status?: string
  severity?: string
  page?: number
  page_size?: number
}) {
  const searchParams = new URLSearchParams()
  if (params?.status) searchParams.set('status', params.status)
  if (params?.severity) searchParams.set('severity', params.severity)
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.page_size) searchParams.set('page_size', String(params.page_size))
  const query = searchParams.toString()

  return useQuery({
    queryKey: ['incidents', params],
    queryFn: () =>
      apiFetch<IncidentListResponse>(`/api/v1/incidents${query ? `?${query}` : ''}`),
  })
}
