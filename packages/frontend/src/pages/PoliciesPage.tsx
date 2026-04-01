import { usePolicies } from '../api/policies'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { SeverityBadge, TierBadge } from '../components/PolicyBadge'
import { formatDistanceToNow } from 'date-fns'

export function PoliciesPage() {
  const { data: policies, isLoading } = usePolicies()

  if (isLoading) return <LoadingSpinner />

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">Policies</h2>
      </div>

      {!policies || policies.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-sm text-gray-500">
          No policies configured. Load the starter policy pack to get started.
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
