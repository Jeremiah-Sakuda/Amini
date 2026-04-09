import { useState } from 'react'
import { useParams, useOutletContext } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import { useSession } from '../api/sessions'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { ErrorBanner } from '../components/ErrorBanner'
import { SessionTimeline } from '../components/SessionTimeline'
import { SeverityBadge } from '../components/PolicyBadge'
import type { ViewMode } from '../components/Layout'

export function SessionDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { viewMode } = useOutletContext<{ viewMode: ViewMode }>()
  const { data: session, isLoading, isError, error } = useSession(id || '')
  const [activeTab, setActiveTab] = useState<'replay' | 'audit'>(
    viewMode === 'compliance' ? 'audit' : 'replay'
  )

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorBanner message={error instanceof Error ? error.message : 'Failed to load session'} />
  if (!session) return <div className="text-sm text-gray-500">Session not found</div>

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">
            Session {session.session_external_id.slice(0, 12)}...
          </h2>
          <p className="text-sm text-gray-500">
            {session.environment} &middot; {session.status} &middot;{' '}
            {formatDistanceToNow(new Date(session.created_at), { addSuffix: true })}
          </p>
        </div>
      </div>

      <div className="flex gap-1 rounded-lg bg-gray-100 p-1 w-fit">
        <button
          onClick={() => setActiveTab('replay')}
          className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${
            activeTab === 'replay'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Decision Replay
        </button>
        <button
          onClick={() => setActiveTab('audit')}
          className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${
            activeTab === 'audit'
              ? 'bg-white text-gray-900 shadow-sm'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Audit & Compliance
        </button>
      </div>

      {activeTab === 'replay' ? (
        <SessionTimeline decisions={session.decisions} />
      ) : (
        <AuditView session={session} />
      )}
    </div>
  )
}

function AuditView({ session }: { session: NonNullable<ReturnType<typeof useSession>['data']> }) {
  const handleExportJson = () => {
    const blob = new Blob([JSON.stringify(session, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `session-${session.session_external_id}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-gray-200 bg-white p-4 space-y-3">
        <h3 className="text-sm font-medium text-gray-700">Session Summary</h3>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-500">Status:</span>{' '}
            <span className="font-medium">{session.status}</span>
          </div>
          <div>
            <span className="text-gray-500">Environment:</span>{' '}
            <span className="font-medium">{session.environment}</span>
          </div>
          <div>
            <span className="text-gray-500">Decisions:</span>{' '}
            <span className="font-medium">{session.decisions.length}</span>
          </div>
          <div>
            <span className="text-gray-500">Violations:</span>{' '}
            <span className="font-medium">{session.violations.length}</span>
          </div>
          {session.terminal_reason && (
            <div className="col-span-2">
              <span className="text-gray-500">Terminal Reason:</span>{' '}
              <span className="font-medium">{session.terminal_reason}</span>
            </div>
          )}
        </div>
      </div>

      {session.violations.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white p-4 space-y-3">
          <h3 className="text-sm font-medium text-gray-700">Policy Violations</h3>
          <div className="space-y-2">
            {session.violations.map((v) => (
              <div
                key={v.id}
                className="flex items-start gap-3 rounded-md border border-gray-100 p-3"
              >
                <SeverityBadge severity={v.severity} />
                <div className="flex-1 text-sm">
                  <p className="font-medium text-gray-900">{v.violation_type}</p>
                  <p className="text-gray-600">{v.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex gap-2">
        <button
          onClick={handleExportJson}
          className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          Export JSON
        </button>
        <button
          className="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-400 cursor-not-allowed"
          title="Coming soon"
          disabled
        >
          Export PDF
        </button>
      </div>
    </div>
  )
}
