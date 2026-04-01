import { useState } from 'react'
import { Bot, Shield, AlertTriangle } from 'lucide-react'
import { useAgentRegistry } from '../api/registry'
import { LoadingSpinner } from '../components/LoadingSpinner'

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  deprecated: 'bg-yellow-100 text-yellow-800',
  shadow: 'bg-red-100 text-red-800',
}

const discoveryColors: Record<string, string> = {
  sdk: 'bg-blue-100 text-blue-800',
  manual: 'bg-gray-100 text-gray-800',
  network: 'bg-purple-100 text-purple-800',
}

export function RegistryPage() {
  const [statusFilter, setStatusFilter] = useState<string>('')
  const { data, isLoading } = useAgentRegistry({
    deployment_status: statusFilter || undefined,
  })

  if (isLoading) return <LoadingSpinner />

  const agents = data?.agents || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Agent Registry</h2>
          <p className="mt-1 text-sm text-gray-500">
            Catalog of all AI agent deployments across the organization
          </p>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <span className="text-gray-500">Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-md border border-gray-300 px-2 py-1 text-sm"
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

      <div className="overflow-hidden rounded-lg border border-gray-200 bg-white">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">Agent</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">Framework</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">Risk Class</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase text-gray-500">Discovery</th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase text-gray-500">Sessions</th>
              <th className="px-4 py-3 text-right text-xs font-medium uppercase text-gray-500">Violations</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {agents.map((agent) => (
              <tr key={agent.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{agent.name || agent.agent_external_id}</p>
                    <p className="text-xs text-gray-500">{agent.agent_external_id}</p>
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">{agent.framework || '-'}</td>
                <td className="px-4 py-3">
                  {agent.risk_class ? (
                    <span className="inline-flex rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
                      {agent.risk_class}
                    </span>
                  ) : (
                    <span className="text-sm text-gray-400">-</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                      statusColors[agent.deployment_status] || 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {agent.deployment_status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                      discoveryColors[agent.discovery_method] || 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {agent.discovery_method}
                  </span>
                </td>
                <td className="px-4 py-3 text-right text-sm text-gray-600">{agent.session_count}</td>
                <td className="px-4 py-3 text-right">
                  <span
                    className={`text-sm font-medium ${
                      agent.violation_count > 0 ? 'text-red-600' : 'text-gray-600'
                    }`}
                  >
                    {agent.violation_count}
                  </span>
                </td>
              </tr>
            ))}
            {agents.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-sm text-gray-500">
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
  blue: 'bg-blue-50 text-blue-600',
  green: 'bg-green-50 text-green-600',
  red: 'bg-red-50 text-red-600',
}

function StatCard({ icon, label, value, color }: { icon: React.ReactNode; label: string; value: number; color: string }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <div className="flex items-center gap-3">
        <div className={`rounded-lg p-2 ${colorMap[color]}`}>{icon}</div>
        <div>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
          <p className="text-xs text-gray-500">{label}</p>
        </div>
      </div>
    </div>
  )
}
