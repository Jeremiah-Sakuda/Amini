import { useState } from 'react'
import { Settings, Database, Shield, Info, Check, AlertTriangle, RefreshCw } from 'lucide-react'
import { apiFetch } from '../api/client'

export function SettingsPage() {
  const [healthStatus, setHealthStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [healthData, setHealthData] = useState<{ status: string } | null>(null)
  const [healthError, setHealthError] = useState<string | null>(null)

  const [cleanupStatus, setCleanupStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [cleanupData, setCleanupData] = useState<{ status: string; deleted: Record<string, number> } | null>(null)
  const [cleanupError, setCleanupError] = useState<string | null>(null)

  const [seedStatus, setSeedStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [seedData, setSeedData] = useState<{ seeded: number; regulations: string[] } | null>(null)
  const [seedError, setSeedError] = useState<string | null>(null)

  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const apiKey = import.meta.env.VITE_API_KEY || 'dev-key'
  const maskedKey = apiKey.length > 6
    ? apiKey.slice(0, 3) + '\u2022'.repeat(apiKey.length - 6) + apiKey.slice(-3)
    : '\u2022'.repeat(apiKey.length)

  const checkHealth = async () => {
    setHealthStatus('loading')
    setHealthError(null)
    try {
      const data = await apiFetch<{ status: string }>('/health')
      setHealthData(data)
      setHealthStatus('success')
    } catch (err) {
      setHealthError(err instanceof Error ? err.message : 'Connection failed')
      setHealthStatus('error')
    }
  }

  const triggerCleanup = async () => {
    setCleanupStatus('loading')
    setCleanupError(null)
    try {
      const data = await apiFetch<{ status: string; deleted: Record<string, number> }>('/api/v1/admin/cleanup', {
        method: 'POST',
      })
      setCleanupData(data)
      setCleanupStatus('success')
    } catch (err) {
      setCleanupError(err instanceof Error ? err.message : 'Cleanup failed')
      setCleanupStatus('error')
    }
  }

  const seedRegulations = async () => {
    setSeedStatus('loading')
    setSeedError(null)
    try {
      const data = await apiFetch<{ seeded: number; regulations: string[] }>('/api/v1/regulations/seed', {
        method: 'POST',
      })
      setSeedData(data)
      setSeedStatus('success')
    } catch (err) {
      setSeedError(err instanceof Error ? err.message : 'Seeding failed')
      setSeedStatus('error')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Settings size={24} className="text-gray-700" />
        <h2 className="text-xl font-semibold text-gray-900">Settings</h2>
      </div>

      {/* Configuration */}
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h3 className="mb-4 flex items-center gap-2 text-sm font-medium text-gray-700">
          <Settings size={16} />
          Configuration
        </h3>
        <div className="space-y-3">
          <ConfigRow label="API Base URL" value={apiBaseUrl} />
          <ConfigRow label="API Key" value={maskedKey} />
          <ConfigRow label="Retention Period" value="90 days" />
        </div>
      </div>

      {/* Connection Status */}
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h3 className="mb-4 flex items-center gap-2 text-sm font-medium text-gray-700">
          <RefreshCw size={16} />
          Connection Status
        </h3>
        <button
          onClick={checkHealth}
          disabled={healthStatus === 'loading'}
          className="flex items-center gap-2 rounded-md bg-amini-600 px-4 py-2 text-sm font-medium text-white hover:bg-amini-700 disabled:opacity-50"
        >
          {healthStatus === 'loading' ? (
            <><RefreshCw size={16} className="animate-spin" /> Checking...</>
          ) : (
            <><RefreshCw size={16} /> Check Backend Health</>
          )}
        </button>
        {healthStatus === 'success' && healthData && (
          <div className="mt-3 flex items-start gap-2 rounded-md bg-green-50 px-3 py-2">
            <Check size={16} className="mt-0.5 flex-shrink-0 text-green-600" />
            <p className="text-sm text-green-900">Backend is healthy (status: {healthData.status})</p>
          </div>
        )}
        {healthStatus === 'error' && (
          <div className="mt-3 flex items-start gap-2 rounded-md bg-red-50 px-3 py-2">
            <AlertTriangle size={16} className="mt-0.5 flex-shrink-0 text-red-600" />
            <p className="text-sm text-red-900">{healthError}</p>
          </div>
        )}
      </div>

      {/* Data Management */}
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h3 className="mb-4 flex items-center gap-2 text-sm font-medium text-gray-700">
          <Database size={16} />
          Data Management
        </h3>
        <div>
          <button
            onClick={triggerCleanup}
            disabled={cleanupStatus === 'loading'}
            className="flex items-center gap-2 rounded-md bg-orange-600 px-4 py-2 text-sm font-medium text-white hover:bg-orange-700 disabled:opacity-50"
          >
            {cleanupStatus === 'loading' ? (
              <><Database size={16} className="animate-spin" /> Running...</>
            ) : (
              <><Database size={16} /> Trigger Retention Cleanup</>
            )}
          </button>
          <p className="mt-1 text-xs text-gray-500">
            Delete data older than the configured retention period
          </p>
        </div>
        {cleanupStatus === 'success' && cleanupData && (
          <div className="mt-3 flex items-start gap-2 rounded-md bg-green-50 px-3 py-2">
            <Check size={16} className="mt-0.5 flex-shrink-0 text-green-600" />
            <div>
              <p className="text-sm font-medium text-green-900">Cleanup completed</p>
              <p className="text-xs text-green-700">
                {Object.entries(cleanupData.deleted).map(([k, v]) => `${k}: ${v}`).join(', ')}
              </p>
            </div>
          </div>
        )}
        {cleanupStatus === 'error' && (
          <div className="mt-3 flex items-start gap-2 rounded-md bg-red-50 px-3 py-2">
            <AlertTriangle size={16} className="mt-0.5 flex-shrink-0 text-red-600" />
            <p className="text-sm text-red-900">{cleanupError}</p>
          </div>
        )}
      </div>

      {/* Regulatory Templates */}
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h3 className="mb-4 flex items-center gap-2 text-sm font-medium text-gray-700">
          <Shield size={16} />
          Regulatory Templates
        </h3>
        <div>
          <button
            onClick={seedRegulations}
            disabled={seedStatus === 'loading'}
            className="flex items-center gap-2 rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50"
          >
            {seedStatus === 'loading' ? (
              <><Shield size={16} className="animate-spin" /> Seeding...</>
            ) : (
              <><Shield size={16} /> Seed Regulatory Frameworks</>
            )}
          </button>
          <p className="mt-1 text-xs text-gray-500">
            Load pre-built templates (EU AI Act, SOC 2 Type II)
          </p>
        </div>
        {seedStatus === 'success' && seedData && (
          <div className="mt-3 flex items-start gap-2 rounded-md bg-green-50 px-3 py-2">
            <Check size={16} className="mt-0.5 flex-shrink-0 text-green-600" />
            <div>
              <p className="text-sm font-medium text-green-900">Seeded {seedData.seeded} frameworks</p>
              <p className="text-xs text-green-700">{seedData.regulations.join(', ')}</p>
            </div>
          </div>
        )}
        {seedStatus === 'error' && (
          <div className="mt-3 flex items-start gap-2 rounded-md bg-red-50 px-3 py-2">
            <AlertTriangle size={16} className="mt-0.5 flex-shrink-0 text-red-600" />
            <p className="text-sm text-red-900">{seedError}</p>
          </div>
        )}
      </div>

      {/* About */}
      <div className="rounded-lg border border-gray-200 bg-white p-4">
        <h3 className="mb-4 flex items-center gap-2 text-sm font-medium text-gray-700">
          <Info size={16} />
          About
        </h3>
        <p className="text-sm font-medium text-gray-900">Amini v2</p>
        <p className="mt-1 text-xs text-gray-600">
          Compliance infrastructure for agentic AI. Real-time monitoring, policy enforcement,
          and audit trails for AI agent systems.
        </p>
      </div>
    </div>
  )
}

function ConfigRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-md bg-gray-50 px-3 py-2">
      <span className="text-sm text-gray-600">{label}</span>
      <span className="font-mono text-xs text-gray-900">{value}</span>
    </div>
  )
}
