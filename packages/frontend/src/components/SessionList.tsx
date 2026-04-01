import { Link } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import type { Session } from '../types/session'
import { SeverityBadge } from './PolicyBadge'

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-700',
  completed: 'bg-gray-100 text-gray-700',
  error: 'bg-red-100 text-red-700',
  timeout: 'bg-yellow-100 text-yellow-700',
  human_handoff: 'bg-blue-100 text-blue-700',
}

export function SessionList({ sessions }: { sessions: Session[] }) {
  if (sessions.length === 0) {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-sm text-gray-500">
        No sessions found. Start tracing an agent to see sessions here.
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">Session</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">Status</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">Environment</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">Decisions</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">Violations</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">Created</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200">
          {sessions.map((session) => (
            <tr key={session.id} className="hover:bg-gray-50">
              <td className="px-4 py-3">
                <Link
                  to={`/sessions/${session.id}`}
                  className="text-sm font-medium text-amini-600 hover:text-amini-800"
                >
                  {session.session_external_id.slice(0, 12)}...
                </Link>
              </td>
              <td className="px-4 py-3">
                <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${statusColors[session.status] || 'bg-gray-100 text-gray-700'}`}>
                  {session.status}
                </span>
              </td>
              <td className="px-4 py-3 text-sm text-gray-600">{session.environment}</td>
              <td className="px-4 py-3 text-sm text-gray-600">{session.decision_count}</td>
              <td className="px-4 py-3">
                {session.violation_count > 0 ? (
                  <SeverityBadge severity="high" />
                ) : (
                  <span className="text-sm text-gray-400">0</span>
                )}
              </td>
              <td className="px-4 py-3 text-sm text-gray-500">
                {formatDistanceToNow(new Date(session.created_at), { addSuffix: true })}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
