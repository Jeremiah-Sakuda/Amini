import { useState } from 'react'
import {
  ArrowDownToLine,
  Brain,
  Zap,
  ArrowUpFromLine,
  AlertCircle,
  ChevronDown,
  ChevronRight,
} from 'lucide-react'
import type { DecisionTreeNode } from '../types/decision'
import type { DecisionNode } from '../types/decision'

type AnyDecisionNode = DecisionTreeNode | DecisionNode

interface Props {
  node: AnyDecisionNode
}

interface PhaseConfig {
  key: string
  label: string
  icon: React.ReactNode
  borderColor: string
  dotColor: string
  getData: (node: AnyDecisionNode) => unknown
  prose?: boolean
}

const phases: PhaseConfig[] = [
  {
    key: 'input',
    label: 'Input',
    icon: <ArrowDownToLine size={14} />,
    borderColor: 'border-blue-500',
    dotColor: 'bg-blue-500',
    getData: (n) => n.input_context,
  },
  {
    key: 'reasoning',
    label: 'Reasoning',
    icon: <Brain size={14} />,
    borderColor: 'border-purple-500',
    dotColor: 'bg-purple-500',
    getData: (n) => n.reasoning_trace,
    prose: true,
  },
  {
    key: 'action',
    label: 'Action',
    icon: <Zap size={14} />,
    borderColor: 'border-amber-500',
    dotColor: 'bg-amber-500',
    getData: (n) => n.action_detail,
  },
  {
    key: 'output',
    label: 'Output',
    icon: <ArrowUpFromLine size={14} />,
    borderColor: 'border-green-500',
    dotColor: 'bg-green-500',
    getData: (n) => n.output,
  },
]

const errorPhase: PhaseConfig = {
  key: 'error',
  label: 'Error',
  icon: <AlertCircle size={14} />,
  borderColor: 'border-red-500',
  dotColor: 'bg-red-500',
  getData: (n) => ('side_effects' in n ? n.side_effects : null),
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

function PipelinePhase({ config, data }: { config: PhaseConfig; data: unknown }) {
  const [jsonExpanded, setJsonExpanded] = useState(false)

  const renderContent = () => {
    if (typeof data === 'string') {
      return (
        <p className={`text-sm text-zinc-300 ${config.prose ? 'whitespace-pre-wrap' : 'font-mono text-xs'}`}>
          {data}
        </p>
      )
    }

    if (data && typeof data === 'object') {
      const entries = Object.entries(data as Record<string, unknown>)
      if (entries.length > 0 && entries.length < 6) {
        return (
          <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-sm">
            {entries.map(([k, v]) => (
              <div key={k} className="contents">
                <dt className="font-medium text-zinc-500 text-xs">{k}</dt>
                <dd className="text-zinc-300 text-xs font-mono truncate">
                  {typeof v === 'string' ? v : JSON.stringify(v)}
                </dd>
              </div>
            ))}
          </dl>
        )
      }

      return (
        <div>
          <button
            onClick={() => setJsonExpanded(!jsonExpanded)}
            className="flex items-center gap-1 text-xs text-zinc-500 hover:text-zinc-300 mb-1"
          >
            {jsonExpanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
            {jsonExpanded ? 'Collapse' : 'Expand'} JSON ({entries.length} keys)
          </button>
          {jsonExpanded && (
            <pre className="text-xs text-zinc-400 font-mono bg-zinc-800 rounded p-2 max-h-48 overflow-auto">
              {JSON.stringify(data, null, 2)}
            </pre>
          )}
        </div>
      )
    }

    return <span className="text-xs text-zinc-600">null</span>
  }

  return (
    <div className={`border-l-2 ${config.borderColor} pl-3 py-2`}>
      <div className="flex items-center gap-2 mb-1.5">
        <span className={`flex items-center justify-center w-5 h-5 rounded-full ${config.dotColor} text-white`}>
          {config.icon}
        </span>
        <span className="text-xs font-semibold text-zinc-400 uppercase tracking-wide">{config.label}</span>
      </div>
      {renderContent()}
    </div>
  )
}

export function DecisionPipelineView({ node }: Props) {
  const activePhases = phases.filter((p) => {
    const d = p.getData(node)
    return d !== null && d !== undefined
  })

  if (node.has_error) {
    const errData = errorPhase.getData(node)
    if (errData !== null && errData !== undefined) {
      activePhases.push(errorPhase)
    }
  }

  if (activePhases.length === 0) {
    return (
      <div className="py-3 px-2 text-xs text-zinc-600 italic">
        No trace data available for this decision.
      </div>
    )
  }

  return (
    <div className="py-3 px-2 space-y-0">
      {node.duration_ms !== null && node.duration_ms !== undefined && (
        <div className="flex items-center gap-2 mb-3">
          <div className="h-1 flex-1 rounded-full bg-zinc-800 overflow-hidden">
            <div
              className="h-full rounded-full bg-indigo-500"
              style={{ width: `${Math.min(100, (node.duration_ms / 2000) * 100)}%` }}
            />
          </div>
          <span className="text-xs text-zinc-500 font-mono whitespace-nowrap">
            {formatDuration(node.duration_ms)}
          </span>
        </div>
      )}

      {activePhases.map((phase, i) => (
        <div key={phase.key}>
          <PipelinePhase config={phase} data={phase.getData(node)} />
          {i < activePhases.length - 1 && (
            <div className="flex justify-center py-1">
              <ChevronDown size={14} className="text-zinc-600" />
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
