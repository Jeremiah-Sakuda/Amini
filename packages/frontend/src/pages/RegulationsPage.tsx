import { useState } from 'react'
import { BookOpen, HelpCircle } from 'lucide-react'
import { useRegulations } from '../api/regulations'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { ErrorBanner } from '../components/ErrorBanner'

export function RegulationsPage() {
  const { data, isLoading, isError, error } = useRegulations()
  const [expandedId, setExpandedId] = useState<string | null>(null)

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorBanner message={error instanceof Error ? error.message : 'Failed to load regulations'} />

  const regulations = data?.regulations || []

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-gray-900">Regulatory Frameworks</h2>
        <p className="mt-1 text-sm text-gray-500">
          Pre-built compliance templates mapped to regulatory requirements
        </p>
      </div>

      <div className="space-y-4">
        {regulations.map((reg) => (
          <div key={reg.id} className="overflow-hidden rounded-lg border border-gray-200 bg-white">
            <button
              onClick={() => setExpandedId(expandedId === reg.id ? null : reg.id)}
              className="flex w-full items-center justify-between px-5 py-4 text-left hover:bg-gray-50"
            >
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-amini-50 p-2 text-amini-600">
                  <BookOpen size={20} />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-gray-900">{reg.name}</h3>
                  <p className="text-xs text-gray-500">
                    {reg.jurisdiction} &middot; {reg.short_code} &middot; v{reg.version}
                    {reg.effective_date && ` &middot; Effective: ${reg.effective_date}`}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700">
                  {reg.requirements.length} requirements
                </span>
                <span
                  className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                    reg.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {reg.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </button>

            {expandedId === reg.id && (
              <div className="border-t border-gray-200 px-5 py-4">
                <p className="mb-4 text-sm text-gray-600">{reg.description}</p>
                <div className="space-y-2">
                  {reg.requirements.map((req) => (
                    <div
                      key={req.id}
                      className="flex items-start gap-3 rounded-md border border-gray-100 bg-gray-50 px-4 py-3"
                    >
                      <div className="mt-0.5 text-gray-400">
                        <HelpCircle size={16} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold text-amini-700">
                            Art. {req.article}
                          </span>
                          {req.section && (
                            <span className="text-xs text-gray-500">{req.section}</span>
                          )}
                        </div>
                        <p className="mt-0.5 text-sm font-medium text-gray-800">{req.title}</p>
                        <p className="mt-1 text-xs text-gray-500">{req.description}</p>
                        <div className="mt-2 flex items-center gap-3 text-xs text-gray-400">
                          {req.applies_to_risk_class && (
                            <span>Risk class: {req.applies_to_risk_class}</span>
                          )}
                          <span>Review: every {req.review_cadence_days} days</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}

        {regulations.length === 0 && (
          <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-sm text-gray-500">
            No regulatory frameworks loaded. Seed templates via the API.
          </div>
        )}
      </div>
    </div>
  )
}
