import { useState } from 'react'
import { AlertOctagon, Clock, CheckCircle2, Search } from 'lucide-react'
import { useIncidents } from '../api/incidents'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { format } from 'date-fns'

const severityColors: Record<string, string> = {
  critical: 'bg-red-100 text-red-800',
  high: 'bg-orange-100 text-orange-800',
  medium: 'bg-yellow-100 text-yellow-800',
  low: 'bg-blue-100 text-blue-800',
}

const statusColors: Record<string, string> = {
  open: 'bg-red-100 text-red-800',
  investigating: 'bg-yellow-100 text-yellow-800',
  remediated: 'bg-blue-100 text-blue-800',
  closed: 'bg-green-100 text-green-800',
  false_positive: 'bg-gray-100 text-gray-800',
}

const statusIcons: Record<string, React.ReactNode> = {
  open: <AlertOctagon size={14} />,
  investigating: <Search size={14} />,
  remediated: <Clock size={14} />,
  closed: <CheckCircle2 size={14} />,
}

export function IncidentsPage() {
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [severityFilter, setSeverityFilter] = useState<string>('')

  const { data, isLoading } = useIncidents({
    status: statusFilter || undefined,
    severity: severityFilter || undefined,
    page,
  })

  if (isLoading) return <LoadingSpinner />

  const incidents = data?.incidents || []
  const total = data?.total || 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Incidents</h2>
          <p className="mt-1 text-sm text-gray-500">
            Policy violation incidents with remediation tracking
          </p>
        </div>
        <div className="flex items-center gap-3 text-sm">
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
            className="rounded-md border border-gray-300 px-2 py-1 text-sm"
          >
            <option value="">All Status</option>
            <option value="open">Open</option>
            <option value="investigating">Investigating</option>
            <option value="remediated">Remediated</option>
            <option value="closed">Closed</option>
          </select>
          <select
            value={severityFilter}
            onChange={(e) => { setSeverityFilter(e.target.value); setPage(1) }}
            className="rounded-md border border-gray-300 px-2 py-1 text-sm"
          >
            <option value="">All Severity</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      <div className="space-y-3">
        {incidents.map((incident) => (
          <div
            key={incident.id}
            className="rounded-lg border border-gray-200 bg-white px-5 py-4"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span
                    className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                      severityColors[incident.severity] || 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {incident.severity}
                  </span>
                  <span
                    className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                      statusColors[incident.status] || 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {statusIcons[incident.status]}
                    {incident.status}
                  </span>
                  {incident.regulation && (
                    <span className="inline-flex rounded-full bg-amini-100 px-2 py-0.5 text-xs font-medium text-amini-800">
                      {incident.regulation}
                      {incident.regulation_article && ` Art. ${incident.regulation_article}`}
                    </span>
                  )}
                </div>
                <h3 className="mt-1 text-sm font-medium text-gray-900">{incident.title}</h3>
                <p className="mt-1 text-xs text-gray-500">
                  Policy: {incident.policy_name || 'Unknown'} &middot;{' '}
                  {format(new Date(incident.created_at), 'MMM d, yyyy HH:mm')}
                </p>
              </div>
            </div>
            {incident.remediation_path && (
              <div className="mt-3 rounded-md bg-gray-50 px-3 py-2">
                <p className="text-xs font-medium text-gray-700">Remediation Path</p>
                <p className="mt-1 whitespace-pre-line text-xs text-gray-500">
                  {incident.remediation_path}
                </p>
              </div>
            )}
          </div>
        ))}

        {incidents.length === 0 && (
          <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-sm text-gray-500">
            No incidents found.
          </div>
        )}
      </div>

      {total > 20 && (
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>Showing {incidents.length} of {total} incidents</span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="rounded-md border px-3 py-1 disabled:opacity-50"
            >
              Previous
            </button>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={incidents.length < 20}
              className="rounded-md border px-3 py-1 disabled:opacity-50"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
