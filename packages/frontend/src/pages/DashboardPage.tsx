import { Activity, AlertTriangle, GitBranch, Clock, Shield, Bot, FileText, AlertOctagon } from 'lucide-react'
import { useOutletContext } from 'react-router-dom'
import { useSessions } from '../api/sessions'
import { useViolations } from '../api/violations'
import { useAgentRegistry } from '../api/registry'
import { useIncidents } from '../api/incidents'
import { useReports } from '../api/reports'
import { useRegulations } from '../api/regulations'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { ErrorBanner } from '../components/ErrorBanner'
import { SessionList } from '../components/SessionList'
import type { ViewMode } from '../components/Layout'

export function DashboardPage() {
  const { viewMode } = useOutletContext<{ viewMode: ViewMode }>()
  const { data: sessionsData, isLoading: sessionsLoading, isError: sessionsError, error: sessionsErr } = useSessions({ page: 1 })
  const { data: violationsData, isLoading: violationsLoading, isError: violationsError, error: violationsErr } = useViolations({ page: 1 })
  const { data: registryData } = useAgentRegistry()
  const { data: incidentsData } = useIncidents({ page: 1 })
  const { data: reportsData } = useReports()
  const { data: regulationsData } = useRegulations()

  if (sessionsLoading || violationsLoading) {
    return <LoadingSpinner />
  }
  if (sessionsError || violationsError) {
    const msg = sessionsErr instanceof Error ? sessionsErr.message
      : violationsErr instanceof Error ? violationsErr.message
      : 'Failed to load dashboard data'
    return <ErrorBanner message={msg} />
  }

  const sessions = sessionsData?.sessions || []
  const totalSessions = sessionsData?.total || 0
  const totalViolations = violationsData?.total || 0
  const activeSessions = sessions.filter((s) => s.status === 'active').length
  const totalDecisions = sessions.reduce((sum, s) => sum + s.decision_count, 0)
  const totalAgents = registryData?.total || 0
  const totalIncidents = incidentsData?.total || 0
  const openIncidents = incidentsData?.incidents?.filter((i) => i.status === 'open').length || 0
  const totalReports = reportsData?.total || 0
  const totalRegulations = regulationsData?.total || 0

  if (viewMode === 'compliance') {
    return (
      <div className="space-y-6">
        <h2 className="text-xl font-semibold text-zinc-100">Compliance Overview</h2>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            icon={<Bot size={20} />}
            label="Registered Agents"
            value={totalAgents}
            color="blue"
          />
          <StatCard
            icon={<Shield size={20} />}
            label="Regulatory Frameworks"
            value={totalRegulations}
            color="green"
          />
          <StatCard
            icon={<AlertOctagon size={20} />}
            label="Open Incidents"
            value={openIncidents}
            color={openIncidents > 0 ? 'red' : 'gray'}
          />
          <StatCard
            icon={<FileText size={20} />}
            label="Audit Reports"
            value={totalReports}
            color="purple"
          />
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
          <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4">
            <h3 className="mb-3 text-sm font-medium text-zinc-300">Risk Summary</h3>
            <div className="space-y-2">
              <RiskRow label="Total Violations" value={totalViolations} color={totalViolations > 0 ? 'red' : 'green'} />
              <RiskRow label="Total Incidents" value={totalIncidents} color={totalIncidents > 0 ? 'orange' : 'green'} />
              <RiskRow label="Agent Sessions Audited" value={totalSessions} color="blue" />
              <RiskRow label="Decision Nodes Captured" value={totalDecisions} color="blue" />
            </div>
          </div>
          <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4">
            <h3 className="mb-3 text-sm font-medium text-zinc-300">Compliance Readiness</h3>
            <div className="space-y-3">
              {(regulationsData?.regulations || []).map((reg) => (
                <div key={reg.id} className="flex items-center justify-between rounded-md bg-zinc-800/50 px-3 py-2">
                  <div>
                    <p className="text-sm font-medium text-zinc-100">{reg.name}</p>
                    <p className="text-xs text-zinc-500">{reg.requirements.length} requirements</p>
                  </div>
                  <span className="text-xs text-zinc-600">
                    {reg.effective_date ? `Effective: ${reg.effective_date}` : ''}
                  </span>
                </div>
              ))}
              {(regulationsData?.regulations || []).length === 0 && (
                <p className="text-sm text-zinc-600">No frameworks loaded</p>
              )}
            </div>
          </div>
        </div>

        <div>
          <h3 className="mb-3 text-sm font-medium text-zinc-300">Recent Sessions</h3>
          <SessionList sessions={sessions.slice(0, 5)} />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-zinc-100">Dashboard</h2>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={<Activity size={20} />}
          label="Total Sessions"
          value={totalSessions}
          color="blue"
        />
        <StatCard
          icon={<Clock size={20} />}
          label="Active Sessions"
          value={activeSessions}
          color="green"
        />
        <StatCard
          icon={<GitBranch size={20} />}
          label="Decision Nodes"
          value={totalDecisions}
          color="purple"
        />
        <StatCard
          icon={<AlertTriangle size={20} />}
          label="Violations"
          value={totalViolations}
          color={totalViolations > 0 ? 'red' : 'gray'}
        />
      </div>

      <div>
        <h3 className="mb-3 text-sm font-medium text-zinc-300">Recent Sessions</h3>
        <SessionList sessions={sessions.slice(0, 10)} />
      </div>
    </div>
  )
}

const colorMap: Record<string, string> = {
  blue: 'bg-blue-500/10 text-blue-400',
  green: 'bg-emerald-500/10 text-emerald-400',
  purple: 'bg-purple-500/10 text-purple-400',
  red: 'bg-red-500/10 text-red-400',
  orange: 'bg-orange-500/10 text-orange-400',
  gray: 'bg-zinc-500/10 text-zinc-400',
}

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode
  label: string
  value: number
  color: string
}) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-4">
      <div className="flex items-center gap-3">
        <div className={`rounded-lg p-2 ${colorMap[color]}`}>{icon}</div>
        <div>
          <p className="text-2xl font-semibold text-zinc-100">{value}</p>
          <p className="text-xs text-zinc-500">{label}</p>
        </div>
      </div>
    </div>
  )
}

const riskColors: Record<string, string> = {
  red: 'text-red-400',
  orange: 'text-orange-400',
  green: 'text-emerald-400',
  blue: 'text-blue-400',
}

function RiskRow({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="flex items-center justify-between rounded-md bg-zinc-800/50 px-3 py-2">
      <span className="text-sm text-zinc-400">{label}</span>
      <span className={`text-sm font-semibold ${riskColors[color]}`}>{value}</span>
    </div>
  )
}
