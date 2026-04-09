import { useState } from 'react'
import { ChevronLeft, ChevronRight, RotateCcw } from 'lucide-react'
import type { DecisionNode } from '../types/decision'
import { DecisionNodeCard } from './DecisionNode'

interface Props {
  decisions: DecisionNode[]
}

export function SessionTimeline({ decisions }: Props) {
  const [activeIndex, setActiveIndex] = useState(0)
  const sorted = [...decisions].sort((a, b) => a.sequence_number - b.sequence_number)

  const goNext = () => setActiveIndex((i) => Math.min(i + 1, sorted.length - 1))
  const goPrev = () => setActiveIndex((i) => Math.max(i - 1, 0))
  const reset = () => setActiveIndex(0)

  if (sorted.length === 0) {
    return (
      <div className="rounded-lg border border-zinc-800 bg-zinc-900 p-8 text-center text-sm text-zinc-500">
        No decisions recorded for this session.
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <span className="text-sm text-zinc-500">
          Step {activeIndex + 1} of {sorted.length}
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
            disabled={activeIndex === 0}
            className="rounded-md p-1.5 text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300 disabled:opacity-30"
          >
            <ChevronLeft size={14} />
          </button>
          <button
            onClick={goNext}
            disabled={activeIndex === sorted.length - 1}
            className="rounded-md p-1.5 text-zinc-500 hover:bg-zinc-800 hover:text-zinc-300 disabled:opacity-30"
          >
            <ChevronRight size={14} />
          </button>
        </div>
      </div>

      <div className="relative space-y-2">
        {sorted.map((node, index) => (
          <div key={node.id} className="relative">
            {index < sorted.length - 1 && (
              <div className="absolute left-5 top-12 h-full w-0.5 bg-zinc-800" />
            )}
            <div className="relative">
              <div
                className={`absolute left-3.5 top-4 h-3 w-3 rounded-full border-2 ${
                  index === activeIndex
                    ? 'border-indigo-500 bg-indigo-500'
                    : index < activeIndex
                    ? 'border-indigo-800 bg-indigo-800'
                    : 'border-zinc-700 bg-zinc-900'
                }`}
              />
              <div className="ml-10">
                <DecisionNodeCard
                  node={node}
                  isActive={index === activeIndex}
                  onClick={() => setActiveIndex(index)}
                />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
