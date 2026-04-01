import { useState } from 'react'
import { ChevronDown, ChevronRight, AlertCircle, Clock, Zap } from 'lucide-react'
import type { DecisionNode as DecisionNodeType } from '../types/decision'
import { SeverityBadge } from './PolicyBadge'

interface Props {
  node: DecisionNodeType
  isActive: boolean
  onClick: () => void
}

export function DecisionNodeCard({ node, isActive, onClick }: Props) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div
      className={`rounded-lg border transition-colors ${
        isActive
          ? 'border-amini-400 bg-amini-50 ring-2 ring-amini-200'
          : node.has_error
          ? 'border-red-200 bg-red-50'
          : 'border-gray-200 bg-white hover:border-gray-300'
      }`}
    >
      <button
        onClick={() => { onClick(); setExpanded(!expanded) }}
        className="flex w-full items-center gap-3 px-4 py-3 text-left"
      >
        {expanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-900 truncate">
              {node.decision_type}
            </span>
            {node.action_type && (
              <span className="flex items-center gap-1 text-xs text-gray-500">
                <Zap size={10} />
                {node.action_type}
              </span>
            )}
          </div>
          <div className="flex items-center gap-3 mt-0.5">
            {node.duration_ms !== null && (
              <span className="flex items-center gap-1 text-xs text-gray-400">
                <Clock size={10} />
                {node.duration_ms}ms
              </span>
            )}
            {node.has_error && (
              <span className="flex items-center gap-1 text-xs text-red-600">
                <AlertCircle size={10} />
                Error
              </span>
            )}
          </div>
        </div>
        <span className="text-xs text-gray-400">#{node.sequence_number}</span>
      </button>

      {expanded && (
        <div className="border-t border-gray-100 px-4 py-3 space-y-3">
          {node.input_context && (
            <CollapsibleSection title="Input">
              <pre className="text-xs text-gray-600 overflow-x-auto">
                {JSON.stringify(node.input_context, null, 2)}
              </pre>
            </CollapsibleSection>
          )}
          {node.reasoning_trace && (
            <CollapsibleSection title="Reasoning">
              <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                {node.reasoning_trace}
              </pre>
            </CollapsibleSection>
          )}
          {node.action_detail && (
            <CollapsibleSection title="Action">
              <pre className="text-xs text-gray-600 overflow-x-auto">
                {JSON.stringify(node.action_detail, null, 2)}
              </pre>
            </CollapsibleSection>
          )}
          {node.output && (
            <CollapsibleSection title="Output">
              <pre className="text-xs text-gray-600 overflow-x-auto">
                {JSON.stringify(node.output, null, 2)}
              </pre>
            </CollapsibleSection>
          )}
          {node.has_error && node.side_effects && (
            <CollapsibleSection title="Error Details">
              <pre className="text-xs text-red-600 overflow-x-auto">
                {JSON.stringify(node.side_effects, null, 2)}
              </pre>
            </CollapsibleSection>
          )}
        </div>
      )}
    </div>
  )
}

function CollapsibleSection({ title, children }: { title: string; children: React.ReactNode }) {
  const [open, setOpen] = useState(true)

  return (
    <div>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1 text-xs font-medium text-gray-500 hover:text-gray-700"
      >
        {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        {title}
      </button>
      {open && <div className="mt-1 ml-4">{children}</div>}
    </div>
  )
}
