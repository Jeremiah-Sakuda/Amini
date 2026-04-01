import { useState } from 'react'
import { FileText, Plus } from 'lucide-react'
import { useReports, useGenerateReport } from '../api/reports'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { format } from 'date-fns'

const statusColors: Record<string, string> = {
  completed: 'bg-green-100 text-green-800',
  generating: 'bg-yellow-100 text-yellow-800',
  failed: 'bg-red-100 text-red-800',
}

export function ReportsPage() {
  const { data, isLoading } = useReports()
  const generateReport = useGenerateReport()
  const [showForm, setShowForm] = useState(false)
  const [framework, setFramework] = useState('eu-ai-act')
  const [periodStart, setPeriodStart] = useState('')
  const [periodEnd, setPeriodEnd] = useState('')
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const handleGenerate = () => {
    if (!periodStart || !periodEnd) return
    generateReport.mutate({
      framework,
      period_start: periodStart,
      period_end: periodEnd,
    })
    setShowForm(false)
  }

  if (isLoading) return <LoadingSpinner />

  const reports = data?.reports || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Audit Reports</h2>
          <p className="mt-1 text-sm text-gray-500">
            Generate and review compliance-ready audit documentation
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-1.5 rounded-lg bg-amini-600 px-3 py-2 text-sm font-medium text-white hover:bg-amini-700"
        >
          <Plus size={16} />
          Generate Report
        </button>
      </div>

      {showForm && (
        <div className="rounded-lg border border-amini-200 bg-amini-50 p-4">
          <h3 className="text-sm font-semibold text-gray-900">New Compliance Report</h3>
          <div className="mt-3 grid grid-cols-3 gap-3">
            <div>
              <label className="block text-xs font-medium text-gray-700">Framework</label>
              <select
                value={framework}
                onChange={(e) => setFramework(e.target.value)}
                className="mt-1 w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm"
              >
                <option value="eu-ai-act">EU AI Act</option>
                <option value="soc2">SOC 2 Type II</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700">Period Start</label>
              <input
                type="date"
                value={periodStart}
                onChange={(e) => setPeriodStart(e.target.value)}
                className="mt-1 w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-gray-700">Period End</label>
              <input
                type="date"
                value={periodEnd}
                onChange={(e) => setPeriodEnd(e.target.value)}
                className="mt-1 w-full rounded-md border border-gray-300 px-2 py-1.5 text-sm"
              />
            </div>
          </div>
          <div className="mt-3 flex justify-end gap-2">
            <button
              onClick={() => setShowForm(false)}
              className="rounded-md border border-gray-300 px-3 py-1.5 text-sm text-gray-700"
            >
              Cancel
            </button>
            <button
              onClick={handleGenerate}
              disabled={!periodStart || !periodEnd || generateReport.isPending}
              className="rounded-md bg-amini-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-amini-700 disabled:opacity-50"
            >
              {generateReport.isPending ? 'Generating...' : 'Generate'}
            </button>
          </div>
        </div>
      )}

      <div className="space-y-3">
        {reports.map((report) => (
          <div
            key={report.id}
            className="rounded-lg border border-gray-200 bg-white"
          >
            <button
              onClick={() => setExpandedId(expandedId === report.id ? null : report.id)}
              className="flex w-full items-center justify-between px-5 py-4 text-left hover:bg-gray-50"
            >
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-gray-100 p-2 text-gray-600">
                  <FileText size={20} />
                </div>
                <div>
                  <h3 className="text-sm font-medium text-gray-900">{report.title}</h3>
                  <p className="text-xs text-gray-500">
                    {report.framework} &middot; {report.period_start} to {report.period_end} &middot;{' '}
                    {format(new Date(report.created_at), 'MMM d, yyyy')}
                  </p>
                </div>
              </div>
              <span
                className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${
                  statusColors[report.status] || 'bg-gray-100 text-gray-800'
                }`}
              >
                {report.status}
              </span>
            </button>

            {expandedId === report.id && report.content && (
              <div className="border-t border-gray-200 px-5 py-4 space-y-4">
                {report.summary && (
                  <div>
                    <h4 className="text-xs font-semibold uppercase text-gray-500">Executive Summary</h4>
                    <p className="mt-1 text-sm text-gray-700">{report.summary}</p>
                  </div>
                )}

                {report.content && typeof report.content === 'object' && (
                  <>
                    {(report.content as any).session_summary && (
                      <div className="grid grid-cols-4 gap-3">
                        {Object.entries((report.content as any).session_summary).map(([key, val]) => (
                          <div key={key} className="rounded-md bg-gray-50 p-3">
                            <p className="text-xs text-gray-500">{key.replace(/_/g, ' ')}</p>
                            <p className="text-lg font-semibold text-gray-900">{String(val)}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    {(report.content as any).violation_summary?.by_severity && (
                      <div>
                        <h4 className="text-xs font-semibold uppercase text-gray-500">Violations by Severity</h4>
                        <div className="mt-2 grid grid-cols-4 gap-2">
                          {Object.entries((report.content as any).violation_summary.by_severity).map(
                            ([severity, count]) => (
                              <div key={severity} className="rounded-md border border-gray-200 p-2 text-center">
                                <p className="text-xs text-gray-500">{severity}</p>
                                <p className="text-lg font-semibold text-gray-900">{String(count)}</p>
                              </div>
                            )
                          )}
                        </div>
                      </div>
                    )}
                  </>
                )}

                {report.gap_analysis && (report.gap_analysis as any).missing_policies?.length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold uppercase text-red-600">Compliance Gaps</h4>
                    <ul className="mt-2 space-y-1">
                      {((report.gap_analysis as any).missing_policies as string[]).map(
                        (gap, i) => (
                          <li key={i} className="flex items-center gap-2 text-sm text-red-700">
                            <span className="h-1.5 w-1.5 rounded-full bg-red-500" />
                            {gap}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}

        {reports.length === 0 && (
          <div className="rounded-lg border border-gray-200 bg-white p-8 text-center text-sm text-gray-500">
            No reports generated yet. Click "Generate Report" to create your first compliance report.
          </div>
        )}
      </div>
    </div>
  )
}
