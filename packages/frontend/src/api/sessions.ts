import { useQuery } from '@tanstack/react-query'
import { apiFetch } from './client'
import type { SessionListResponse, SessionDetail } from '../types/session'
import type { DecisionTreeResponse } from '../types/decision'

export function useSessions(params?: {
  page?: number
  agent_id?: string
  environment?: string
  status?: string
}) {
  const searchParams = new URLSearchParams()
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.agent_id) searchParams.set('agent_id', params.agent_id)
  if (params?.environment) searchParams.set('environment', params.environment)
  if (params?.status) searchParams.set('status', params.status)
  const qs = searchParams.toString()

  return useQuery({
    queryKey: ['sessions', params],
    queryFn: () => apiFetch<SessionListResponse>(`/api/v1/sessions${qs ? `?${qs}` : ''}`),
  })
}

export function useSession(id: string) {
  return useQuery({
    queryKey: ['session', id],
    queryFn: () => apiFetch<SessionDetail>(`/api/v1/sessions/${id}`),
    enabled: !!id,
  })
}

export function useDecisionTree(sessionId: string) {
  return useQuery({
    queryKey: ['decisionTree', sessionId],
    queryFn: () => apiFetch<DecisionTreeResponse>(`/api/v1/sessions/${sessionId}/decisions/tree`),
    enabled: !!sessionId,
  })
}
