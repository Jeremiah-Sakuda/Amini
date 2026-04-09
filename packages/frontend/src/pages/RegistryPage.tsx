import { useState } from 'react'
import { Bot, Shield, AlertTriangle } from 'lucide-react'
import { useAgentRegistry } from '../api/registry'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { ErrorBanner } from '../components/ErrorBanner'

const statusColors: Record<string, string> = {
  active: 'bg-emerald-500/10 text-emerald-400',
  inactive: 'bg-zinc-500/10 text-zinc-400',
  deprecated: 'bg-amber-500/10 text-amber-400',
  shadow: 'bg-red-500/10 text-red-400',
}

const discoveryColors: Record<string, string> = {
  sdk: 'bg-blue-500/10 text-blue-400',
  manual: 'bg-zinc-500/10 text-zinc-400',
  network: 'bg-purple-500/10 text-purple-400',
}

export function RegistryPage() {
  const [statusFilter, setStatusFilter] = useState<string>('')
  const { data, isLoading, isError, error } = useAgentRegistry({
    deployment_status: statusFilter || undefined,
  })

  if (isLoading) return <LoadingSpinner />
  if (isError) return <ErrorBanner message={error instanceof Error ? error.message : 'Failed to load agent registry'} />

  const agents = data?.agents || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-zinc-100">Agent Registry</h2>
          <p className="mt-1 text-sm text-zinc-500">
            Catalog of all AI agent deployments across the organization
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span className="text-zinc-500">Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-md border border-zinc-700 bg-zinc-800 px-2 py-1 text-sm text-zinc-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500/20"
          >
            <option value="">All</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="deprecated">Deprecated</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <StatCard
          icon={<Bot size={20} />}
          label="Total Agents"
          value={agents.length}
          color="blue"
        />
        <StatCard
          icon={<Shield size={20} />}
          label="With Regulations"
          value={agents.filter((a) => a.regulations && a.regulations.length > 0).length}
          color="green"
        />
        <StatCard
          icon={<AlertTriangle size={20} />}
          label="Total Violations"
          value={agents.reduce((sum, a) => sum + a.violation_count, 0)}
          color="red"
        />
      </div>

      <div className="overflow-hidden rounded-lg border border-zinc-800 bg-zinc-900">
        <table className="min-w-full">
          <thead>
            <tr className="border-b border-zinc-800">
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-zinc-500">Agent</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-zinc-500">Framework</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-zinc-500">Risk Class</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-zinc-500">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-zinc-500">Discovery</th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase text-zinc-500">Sessions</th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase text-zinc-500">Violations</th>
            </tr>
          </thead>
          <tbody>
            {agents.map((agent) => (
              <tr key={agent.id} className="border-b border-zinc-800/50 hover:bg-zinc-800/50">
                <td className="px-4 py-3">
                  <div>
                    <p className="text-sm font-medium text-zinc-100">{agent.name || agent.agent_external_id}</p>
                    <p className="text-xs text-zinc-500">{agent.agent_external_id}</p>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-zinc-400">{agent.framework || '-'}</td>
                <td className="px-4 py-3">
                  {agent.risk_class ? (
                    <span className="inline-flex rounded-full bg-amber-500/10 px-2 py-0.5 text-xs font-medium text-amber-400">
                      {agent.risk_class}
                    </span>
                  ) : (
                    <span className="text-sm text-zinc-600">-</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                      statusColors[agent.deployment_status] || 'bg-zinc-500/10 text-zinc-400'
                    }`}
                  >
                    {agent.deployment_status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                      discoveryColors[agent.discovery_method] || 'bg-zinc-500/10 text-zinc-400'
                    }`}
                  >
                    {agent.discovery_method}
                  </span>
                </td>
                <td className="px-4 py-3 text-right text-sm text-zinc-400">{agent.session_count}</td>
                <td className="px-4 py-3 text-right">
                  <span
                    className={`text-sm font-medium ${
                      agent.violation_count > 0 ? 'text-red-400' : 'text-zinc-400'
                    }`}
                  >
                    {agent.violation_count}
                  </span>
                </td>
              </tr>
            ))}
            {agents.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-sm text-zinc-500">
                  No agents registered yet. Install the SDK to begin tracking agents.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

const colorMap: Record<string, string> = {
  blue: 'bg-blue-500/10 text-blue-400',
  green: 'bg-emerald-500/10 text-emerald-400',
  red: 'bg-red-500/10 text-red-400',
}

function StatCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: number; color: string }) {
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
