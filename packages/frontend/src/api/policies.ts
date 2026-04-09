import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { apiFetch } from './client'
import type { Policy } from '../types/policy'

export interface CreatePolicyRequest {
  name: string
  description: string
  yaml_content: string
  tier: 'deterministic' | 'semantic'
  enforcement: 'block' | 'warn' | 'log_only'
  severity: 'low' | 'medium' | 'high' | 'critical'
  regulation?: string
  regulation_article?: string
}

export function usePolicies() {
  return useQuery({
    queryKey: ['policies'],
    queryFn: () => apiFetch<Policy[]>('/api/v1/policies'),
  })
}

export function usePolicy(id: string) {
  return useQuery({
    queryKey: ['policy', id],
    queryFn: () => apiFetch<Policy>(`/api/v1/policies/${id}`),
    enabled: !!id,
  })
}

export function useCreatePolicy() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreatePolicyRequest) =>
      apiFetch<Policy>('/api/v1/policies', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['policies'] })
    },
  })
}
