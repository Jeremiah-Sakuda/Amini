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
        <h2 className="text-xl font-semibold text-zinc-100">Violations</h2>
        <select
          value={severity}
          onChange={(e) => { setSeverity(e.target.value); setPage(1) }}
          className="rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500/20"
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
        <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-8 text-center text-sm text-zinc-500">
          No violations found. Policies will flag violations as sessions are processed.
        </div>
      ) : (
        <>
          <div className="space-y-2">
            {data.violations.map((v) => (
              <div
                key={v.id}
                className="rounded-lg border border-zinc-800 bg-zinc-900 p-4"
              >
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <SeverityBadge severity={v.severity} />
                      <span className="text-sm font-medium text-zinc-100">
                        {v.violation_type}
                      </span>
                    </div>
                    <p className="text-sm text-zinc-400">{v.description}</p>
                    <div className="flex items-center gap-2 text-xs text-zinc-600">
                      <Link
                        to={`/sessions/${v.session_id}`}
                        className="text-indigo-400 hover:text-indigo-300"
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
            <div className="flex items-center justify-between border-t border-zinc-800 pt-4">
              <p className="text-sm text-zinc-500">
                Page {page} of {totalPages} ({data.total} total)
              </p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="inline-flex items-center gap-1 rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm font-medium text-zinc-300 hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </button>
                <button
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page >= totalPages}
                  className="inline-flex items-center gap-1 rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm font-medium text-zinc-300 hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-50"
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
