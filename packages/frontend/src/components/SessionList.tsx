import { Link } from 'react-router-dom'
import { formatDistanceToNow } from 'date-fns'
import type { Session } from '../types/session'
import { SeverityBadge } from './PolicyBadge'

const statusColors: Record<string, string> = {
  active: 'bg-emerald-500/10 text-emerald-400',
  completed: 'bg-zinc-500/10 text-zinc-400',
  error: 'bg-red-500/10 text-red-400',
  timeout: 'bg-amber-500/10 text-amber-400',
  human_handoff: 'bg-blue-500/10 text-blue-400',
}

export function SessionList({ sessions }: { sessions: Session[] }) {
  if (sessions.length === 0) {
    return (
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-8 text-center text-sm text-zinc-500">
        No sessions found. Start tracing an agent to see sessions here.
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-lg border border-zinc-800 bg-zinc-900">
      <table className="min-w-full">
        <thead>
          <tr className="border-b border-zinc-800">
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-zinc-500">Session</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-zinc-500">Status</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-zinc-500">Environment</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-zinc-500">Decisions</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-zinc-500">Violations</th>
            <th className="px-4 py-3 text-left text-xs font-medium uppercase text-zinc-500">Created</th>
          </tr>
        </thead>
        <tbody>
          {sessions.map((session) => (
            <tr key={session.id} className="border-b border-zinc-800/50 hover:bg-zinc-800/50">
              <td className="px-4 py-3">
                <Link
                  to={`/sessions/${session.id}`}
                  className="text-sm font-medium text-indigo-400 hover:text-indigo-300"
                >
                  {session.session_external_id.slice(0, 12)}...
                </Link>
              </td>
              <td className="px-4 py-3">
                <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${statusColors[session.status] || 'bg-zinc-500/10 text-zinc-400'}`}>
                  {session.status}
                </span>
              </td>
              <td className="px-4 py-3 text-sm text-zinc-400">{session.environment}</td>
              <td className="px-4 py-3 text-sm text-zinc-400">{session.decision_count}</td>
              <td className="px-4 py-3">
                {session.violation_count > 0 ? (
                  <SeverityBadge severity="high" />
                ) : (
                  <span className="text-sm text-zinc-600">0</span>
                )}
              </td>
              <td className="px-4 py-3 text-sm text-zinc-500">
                {formatDistanceToNow(new Date(session.created_at), { addSuffix: true })}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
