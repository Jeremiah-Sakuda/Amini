import { useState } from 'react'
import { usePolicies, useCreatePolicy } from '../api/policies'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { ErrorBanner } from '../components/ErrorBanner'
import { SeverityBadge, TierBadge } from '../components/PolicyBadge'
import { formatDistanceToNow } from 'date-fns'

export function PoliciesPage() {
  const { data: policies, isLoading, isError, error } = usePolicies()
  const createPolicy = useCreatePolicy()
  const [showCreateForm, setShowCreateForm] = useState(false)

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    yaml_content: '',
    tier: 'deterministic' as const,
    enforcement: 'log_only' as const,
    severity: 'medium' as const,
    regulation: '',
    regulation_article: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const payload = {
        ...formData,
        regulation: formData.regulation || undefined,
        regulation_article: formData.regulation_article || undefined,
      }
      await createPolicy.mutateAsync(payload)
      setShowCreateForm(false)
      setFormData({
        name: '',
        description: '',
        yaml_content: '',
        tier: 'deterministic',
        enforcement: 'log_only',
        severity: 'medium',
        regulation: '',
        regulation_article: '',
      })
    } catch {
      // error is displayed via createPolicy.isError
    }
  }

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorBanner message={error instanceof Error ? error.message : 'Failed to load policies'} />

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">Policies</h2>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="rounded-lg bg-amini-600 px-4 py-2 text-sm font-medium text-white hover:bg-amini-700"
        >
          {showCreateForm ? 'Cancel' : 'Create Policy'}
        </button>
      </div>

      {showCreateForm && (
        <div className="rounded-lg border border-gray-200 bg-white p-4">
          <h3 className="mb-4 text-sm font-semibold text-gray-900">Create New Policy</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Name
              </label>
              <input
                id="name"
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-amini-500 focus:outline-none focus:ring-1 focus:ring-amini-500"
              />
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                id="description"
                rows={2}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-amini-500 focus:outline-none focus:ring-1 focus:ring-amini-500"
              />
            </div>

            <div>
              <label htmlFor="yaml_content" className="block text-sm font-medium text-gray-700">
                Rule Definition (YAML)
              </label>
              <textarea
                id="yaml_content"
                required
                rows={6}
                value={formData.yaml_content}
                onChange={(e) => setFormData({ ...formData, yaml_content: e.target.value })}
                className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 font-mono text-sm focus:border-amini-500 focus:outline-none focus:ring-1 focus:ring-amini-500"
                placeholder={'condition:\n  field: action_type\n  operator: equals\n  value: "blocked_action"\nmessage: "Action was blocked by policy"'}
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label htmlFor="tier" className="block text-sm font-medium text-gray-700">
                  Tier
                </label>
                <select
                  id="tier"
                  value={formData.tier}
                  onChange={(e) => setFormData({ ...formData, tier: e.target.value as 'deterministic' | 'semantic' })}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-amini-500 focus:outline-none focus:ring-1 focus:ring-amini-500"
                >
                  <option value="deterministic">Deterministic</option>
                  <option value="semantic">Semantic</option>
                </select>
              </div>

              <div>
                <label htmlFor="enforcement" className="block text-sm font-medium text-gray-700">
                  Enforcement
                </label>
                <select
                  id="enforcement"
                  value={formData.enforcement}
                  onChange={(e) => setFormData({ ...formData, enforcement: e.target.value as 'block' | 'warn' | 'log_only' })}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-amini-500 focus:outline-none focus:ring-1 focus:ring-amini-500"
                >
                  <option value="log_only">Log Only</option>
                  <option value="warn">Warn</option>
                  <option value="block">Block</option>
                </select>
              </div>

              <div>
                <label htmlFor="severity" className="block text-sm font-medium text-gray-700">
                  Severity
                </label>
                <select
                  id="severity"
                  value={formData.severity}
                  onChange={(e) => setFormData({ ...formData, severity: e.target.value as 'low' | 'medium' | 'high' | 'critical' })}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-amini-500 focus:outline-none focus:ring-1 focus:ring-amini-500"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="regulation" className="block text-sm font-medium text-gray-700">
                  Regulation (optional)
                </label>
                <input
                  id="regulation"
                  type="text"
                  value={formData.regulation}
                  onChange={(e) => setFormData({ ...formData, regulation: e.target.value })}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-amini-500 focus:outline-none focus:ring-1 focus:ring-amini-500"
                  placeholder="e.g., EU AI Act"
                />
              </div>

              <div>
                <label htmlFor="regulation_article" className="block text-sm font-medium text-gray-700">
                  Regulation Article (optional)
                </label>
                <input
                  id="regulation_article"
                  type="text"
                  value={formData.regulation_article}
                  onChange={(e) => setFormData({ ...formData, regulation_article: e.target.value })}
                  className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-amini-500 focus:outline-none focus:ring-1 focus:ring-amini-500"
                  placeholder="e.g., Article 10"
                />
              </div>
            </div>

            {createPolicy.isError && (
              <ErrorBanner
                message={createPolicy.error instanceof Error ? createPolicy.error.message : 'Failed to create policy'}
              />
            )}

            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowCreateForm(false)}
                className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createPolicy.isPending}
                className="rounded-lg bg-amini-600 px-4 py-2 text-sm font-medium text-white hover:bg-amini-700 disabled:opacity-50"
              >
                {createPolicy.isPending ? 'Creating...' : 'Create Policy'}
              </button>
            </div>
          </form>
        </div>
      )}

      {!policies || policies.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-sm text-gray-500">
          No policies configured. Create one above to get started.
        </div>
      ) : (
        <div className="grid gap-3">
          {policies.map((policy) => (
            <div
              key={policy.id}
              className="rounded-lg border border-gray-200 bg-white p-4"
            >
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-sm font-medium text-gray-900">{policy.name}</h3>
                    {policy.latest_version && (
                      <>
                        <TierBadge tier={policy.latest_version.tier} />
                        <SeverityBadge severity={policy.latest_version.severity} />
                      </>
                    )}
                  </div>
                  <p className="text-sm text-gray-600">{policy.description}</p>
                  {policy.latest_version && (
                    <p className="text-xs text-gray-400">
                      v{policy.latest_version.version_number} &middot;{' '}
                      {policy.latest_version.enforcement} &middot;{' '}
                      {formatDistanceToNow(new Date(policy.created_at), { addSuffix: true })}
                    </p>
                  )}
                </div>
                <div
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    policy.is_active
                      ? 'bg-green-100 text-green-700'
                      : 'bg-gray-100 text-gray-500'
                  }`}
                >
                  {policy.is_active ? 'Active' : 'Inactive'}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
