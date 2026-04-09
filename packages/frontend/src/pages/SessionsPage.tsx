import { useState } from 'react'
import { useSessions } from '../api/sessions'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { ErrorBanner } from '../components/ErrorBanner'
import { SessionList } from '../components/SessionList'

export function SessionsPage() {
  const [page, setPage] = useState(1)
  const [environment, setEnvironment] = useState('')
  const [status, setStatus] = useState('')

  const { data, isLoading, isError, error } = useSessions({
    page,
    environment: environment || undefined,
    status: status || undefined,
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-semibold text-zinc-100">Sessions</h2>
        <div className="flex items-center gap-2">
          <select
            value={environment}
            onChange={(e) => { setEnvironment(e.target.value); setPage(1) }}
            className="rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500/20"
          >
            <option value="">All Environments</option>
            <option value="production">Production</option>
            <option value="staging">Staging</option>
            <option value="development">Development</option>
          </select>
          <select
            value={status}
            onChange={(e) => { setStatus(e.target.value); setPage(1) }}
            className="rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500/20"
          >
            <option value="">All Statuses</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="error">Error</option>
            <option value="timeout">Timeout</option>
            <option value="human_handoff">Human Handoff</option>
          </select>
        </div>
      </div>

      {isError ? (
        <ErrorBanner message={error instanceof Error ? error.message : 'Failed to load sessions'} />
      ) : isLoading ? (
        <LoadingSpinner />
      ) : (
        <>
          <SessionList sessions={data?.sessions || []} />
          {data && data.total > 20 && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-zinc-500">
                Page {data.page} of {Math.ceil(data.total / data.page_size)}
              </span>
              <div className="flex gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-300 hover:bg-zinc-700 disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage((p) => p + 1)}
                  disabled={page * 20 >= data.total}
                  className="rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-300 hover:bg-zinc-700 disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
