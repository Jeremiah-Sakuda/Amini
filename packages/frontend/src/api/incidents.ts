import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiFetch } from './client'
import type { IncidentListResponse, Incident } from '../types/incident'

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

export function useUpdateIncident() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({
      id,
      status,
      resolution_notes,
      remediation_path,
    }: {
      id: string
      status?: string
      resolution_notes?: string
      remediation_path?: string
    }) => {
      const body: Record<string, string> = {}
      if (status !== undefined) body.status = status
      if (resolution_notes !== undefined) body.resolution_notes = resolution_notes
      if (remediation_path !== undefined) body.remediation_path = remediation_path

      return apiFetch<Incident>(`/api/v1/incidents/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(body),
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['incidents'] })
    },
  })
}
