import { useQuery } from '@tanstack/react-query'
import { apiFetch } from './client'
import type { Policy } from '../types/policy'

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
