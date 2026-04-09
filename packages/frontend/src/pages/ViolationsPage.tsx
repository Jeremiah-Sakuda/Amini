import { useState } from 'react'
import { Link } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import { ChevronLeft, ChevronRight } from 'lucide-react'
import { useViolations } from '../api/violations'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { ErrorBanner } from '../components/ErrorBanner'
import { SeverityBadge } from '../components/PolicyBadge'

export function ViolationsPage() {
  const [page, setPage] = useState(1)
  const [severity, setSeverity] = useState('')

  const { data, isLoading, isError, error } = useViolations({
    page,
    severity: severity || undefined,
  })

  const pageSize = 20
  const totalPages = data ? Math.ceil(data.total / pageSize) : 0

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-gray-900">Violations</h2>
        <select
          value={severity}
          onChange={(e) => { setSeverity(e.target.value); setPage(1) }}
          className="rounded-md border border-gray-300 px-3 py-1.5 text-sm"
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      {isError ? (
        <ErrorBanner message={error instanceof Error ? error.message : 'Failed to load violations'} />
      ) : isLoading ? (
        <LoadingSpinner />
      ) : !data || data.violations.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-sm text-gray-500">
          No violations found. Policies will flag violations as sessions are processed.
        </div>
      ) : (
        <>
          <div className="space-y-2">
            {data.violations.map((v) => (
              <div
                key={v.id}
                className="rounded-lg border border-gray-200 bg-white p-4"
              >
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <SeverityBadge severity={v.severity} />
                      <span className="text-sm font-medium text-gray-900">
                        {v.violation_type}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600">{v.description}</p>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <Link
                        to={`/sessions/${v.session_id}`}
                        className="text-amini-600 hover:text-amini-800"
                      >
                        View Session
                      </Link>
                      <span>&middot;</span>
                      <span>
                        {formatDistanceToNow(new Date(v.created_at), { addSuffix: true })}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between border-t border-gray-200 pt-4">
              <p className="text-sm text-gray-500">
                Page {page} of {totalPages} ({data.total} total)
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="inline-flex items-center gap-1 rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </button>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="inline-flex items-center gap-1 rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
