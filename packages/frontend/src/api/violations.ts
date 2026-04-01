import { useQuery } from '@tanstack/react-query'
import { apiFetch } from './client'
import type { ViolationListResponse } from '../types/violation'

export function useViolations(params?: {
  page?: number
  session_id?: string
  severity?: string
}) {
  const searchParams = new URLSearchParams()
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.session_id) searchParams.set('session_id', params.session_id)
  if (params?.severity) searchParams.set('severity', params.severity)
  const qs = searchParams.toString()

  return useQuery({
    queryKey: ['violations', params],
    queryFn: () => apiFetch<ViolationListResponse>(`/api/v1/violations${qs ? `?${qs}` : ''}`),
  })
}
