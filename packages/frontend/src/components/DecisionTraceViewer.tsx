import { useState, useMemo, useCallback } from 'react'
import { ChevronLeft, ChevronRight, RotateCcw } from 'lucide-react'
import { useDecisionTree } from '../api/sessions'
import { DecisionTreeNodeRow } from './DecisionTreeNodeRow'
import type { DecisionNode, DecisionTreeNode } from '../types/decision'

interface Props {
  sessionId: string
  decisions: DecisionNode[]
}

function buildTreeFromFlat(decisions: DecisionNode[]): DecisionTreeNode[] {
  const nodeMap = new Map<string, DecisionTreeNode>()
  const roots: DecisionTreeNode[] = []

  const sorted = [...decisions].sort((a, b) => a.sequence_number - b.sequence_number)

  for (const d of sorted) {
    const treeNode: DecisionTreeNode = {
      id: d.id,
      decision_external_id: d.decision_external_id,
      decision_type: d.decision_type,
      sequence_number: d.sequence_number,
      parent_decision_id: d.parent_decision_id,
      action_type: d.action_type,
      duration_ms: d.duration_ms,
      has_error: d.has_error,
      policy_summary: d.policy_summary,
      input_context: d.input_context,
      reasoning_trace: d.reasoning_trace,
      action_detail: d.action_detail,
      output: d.output,
      created_at: d.created_at,
      children: [],
    }
    nodeMap.set(d.id, treeNode)
  }

  for (const d of sorted) {
    const treeNode = nodeMap.get(d.id)!
    if (d.parent_decision_id && nodeMap.has(d.parent_decision_id)) {
      nodeMap.get(d.parent_decision_id)!.children.push(treeNode)
    } else {
      roots.push(treeNode)
    }
  }

  return roots
}

function flattenDFS(nodes: DecisionTreeNode[]): string[] {
  const result: string[] = []
  function walk(node: DecisionTreeNode) {
    result.push(node.id)
    for (const child of node.children) {
      walk(child)
    }
  }
  for (const root of nodes) {
    walk(root)
  }
  return result
}

export function DecisionTraceViewer({ sessionId, decisions }: Props) {
  const { data: treeData } = useDecisionTree(sessionId)

  const roots = useMemo(() => {
    if (treeData?.roots && treeData.roots.length > 0) {
      return treeData.roots
    }
    return buildTreeFromFlat(decisions)
  }, [treeData, decisions])

  const flatOrder = useMemo(() => flattenDFS(roots), [roots])

  const [activeNodeId, setActiveNodeId] = useState<string | null>(
    flatOrder.length > 0 ? flatOrder[0] : null
  )
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())

  const activeIndex = activeNodeId ? flatOrder.indexOf(activeNodeId) : -1

  const toggleExpand = useCallback((id: string) => {
    setExpandedNodes((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }, [])

  const activateNode = useCallback((id: string) => {
    setActiveNodeId(id)
  }, [])

  const goNext = useCallback(() => {
    if (activeIndex < flatOrder.length - 1) {
      const nextId = flatOrder[activeIndex + 1]
      setActiveNodeId(nextId)
      setExpandedNodes((prev) => new Set(prev).add(nextId))
    }
  }, [activeIndex, flatOrder])

  const goPrev = useCallback(() => {
    if (activeIndex > 0) {
      const prevId = flatOrder[activeIndex - 1]
      setActiveNodeId(prevId)
      setExpandedNodes((prev) => new Set(prev).add(prevId))
    }
  }, [activeIndex, flatOrder])

  const reset = useCallback(() => {
    if (flatOrder.length > 0) {
      setActiveNodeId(flatOrder[0])
      setExpandedNodes(new Set())
    }
  }, [flatOrder])

  if (roots.length === 0) {
    return (
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-8 text-center text-sm text-zinc-500">
        No decisions recorded for this session.
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Step-through controls */}
      <div className="flex items-center justify-between">
        <span className="text-sm text-zinc-500">
          Step {activeIndex + 1} of {flatOrder.length}
        </span>
        <div className="flex items-center gap-2">
          <button
            onClick={reset}
            className="rounded-md p-1.5 text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300"
            title="Reset"
          >
            <RotateCcw size={14} />
          </button>
          <button
            onClick={goPrev}
            disabled={activeIndex <= 0}
            className="rounded-md p-1.5 text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300 disabled:opacity-30"
          >
            <ChevronLeft size={14} />
          </button>
          <button
            onClick={goNext}
            disabled={activeIndex >= flatOrder.length - 1}
            className="rounded-md p-1.5 text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300 disabled:opacity-30"
          >
            <ChevronRight size={14} />
          </button>
        </div>
      </div>

      {/* Tree */}
      <div className="relative space-y-1 overflow-x-auto">
        {roots.map((root, i) => (
          <DecisionTreeNodeRow
            key={root.id}
            node={root}
            depth={0}
            isLastChild={i === roots.length - 1}
            parentIsLastStack={[]}
            activeNodeId={activeNodeId}
            expandedNodes={expandedNodes}
            onActivate={activateNode}
            onToggleExpand={toggleExpand}
          />
        ))}
      </div>
    </div>
  )
}
