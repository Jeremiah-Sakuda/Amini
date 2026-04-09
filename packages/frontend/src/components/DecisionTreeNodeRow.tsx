import { ChevronRight, ChevronDown, AlertCircle, Clock, Zap } from 'lucide-react'
import { DecisionPipelineView } from './DecisionPipelineView'
import type { DecisionTreeNode } from '../types/decision'

interface Props {
  node: DecisionTreeNode
  depth: number
  isLastChild: boolean
  parentIsLastStack: boolean[]
  activeNodeId: string | null
  expandedNodes: Set<string>
  onActivate: (id: string) => void
  onToggleExpand: (id: string) => void
}

export function DecisionTreeNodeRow({
  node,
  depth,
  isLastChild,
  parentIsLastStack,
  activeNodeId,
  expandedNodes,
  onActivate,
  onToggleExpand,
}: Props) {
  const hasChildren = node.children.length > 0
  const isActive = activeNodeId === node.id
  const isExpanded = expandedNodes.has(node.id)
  const indent = depth * 28

  return (
    <div className="relative">
      {/* Ancestor vertical connector lines */}
      {parentIsLastStack.map((isLast, i) =>
        isLast ? null : (
          <div
            key={i}
            className="absolute top-0 bottom-0 w-px bg-zinc-700"
            style={{ left: i * 28 + 10 }}
          />
        )
      )}

      {/* Vertical line from parent to this node (half-height if last child) */}
      {depth > 0 && (
        <div
          className="absolute w-px bg-zinc-700"
          style={{
            left: (depth - 1) * 28 + 10,
            top: 0,
            height: isLastChild ? 20 : '100%',
          }}
        />
      )}

      {/* Horizontal branch connector */}
      {depth > 0 && (
        <div
          className="absolute h-px bg-zinc-700"
          style={{
            left: (depth - 1) * 28 + 10,
            top: 20,
            width: 18,
          }}
        />
      )}

      {/* Node row */}
      <div style={{ paddingLeft: indent }}>
        <div
          className={`group flex items-center gap-2 rounded-lg border transition-colors cursor-pointer ${
            isActive
              ? 'border-indigo-500 bg-indigo-500/10 ring-2 ring-indigo-500/20'
              : node.has_error
              ? 'border-red-500/30 bg-red-500/5 hover:border-red-500/50'
              : 'border-zinc-800 bg-zinc-900 hover:border-zinc-700'
          }`}
        >
          {/* Expand/collapse chevron */}
          <button
            onClick={(e) => {
              e.stopPropagation()
              onToggleExpand(node.id)
            }}
            className="flex items-center justify-center w-8 h-full py-3 pl-2 text-zinc-500 hover:text-zinc-300 shrink-0"
            aria-label={isExpanded ? 'Collapse' : 'Expand'}
          >
            {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          </button>

          {/* Clickable header area */}
          <div
            className="flex items-center gap-3 flex-1 min-w-0 py-3 pr-4"
            onClick={() => onActivate(node.id)}
          >
            {/* Colored dot */}
            <div
              className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                isActive
                  ? 'bg-indigo-500'
                  : node.has_error
                  ? 'bg-red-400'
                  : hasChildren
                  ? 'bg-indigo-400'
                  : 'bg-zinc-600'
              }`}
            />

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-zinc-100 truncate">
                  {node.decision_type}
                </span>
                {node.action_type && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400">
                    <Zap size={10} />
                    {node.action_type}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-3 mt-0.5">
                {node.duration_ms !== null && (
                  <span className="flex items-center gap-1 text-xs text-zinc-500">
                    <Clock size={10} />
                    {node.duration_ms}ms
                  </span>
                )}
                {node.has_error && (
                  <span className="flex items-center gap-1 text-xs text-red-400">
                    <AlertCircle size={10} />
                    Error
                  </span>
                )}
              </div>
            </div>

            <span className="text-xs text-zinc-500 shrink-0">#{node.sequence_number}</span>
          </div>
        </div>

        {/* Expanded pipeline view with CSS transition */}
        <div
          className={`grid transition-[grid-template-rows] duration-200 ease-in-out ${
            isExpanded ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'
          }`}
        >
          <div className="overflow-hidden">
            {isExpanded && (
              <div className="ml-4 border-l border-zinc-800">
                <DecisionPipelineView node={node} />
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Recursive children */}
      {hasChildren && isExpanded && (
        <div>
          {node.children.map((child, i) => (
            <DecisionTreeNodeRow
              key={child.id}
              node={child}
              depth={depth + 1}
              isLastChild={i === node.children.length - 1}
              parentIsLastStack={[...parentIsLastStack, isLastChild]}
              activeNodeId={activeNodeId}
              expandedNodes={expandedNodes}
              onActivate={onActivate}
              onToggleExpand={onToggleExpand}
            />
          ))}
        </div>
      )}
    </div>
  )
}
