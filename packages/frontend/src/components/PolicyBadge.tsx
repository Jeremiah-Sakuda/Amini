const severityColors: Record<string, string> = {
  low: 'bg-blue-500/10 text-blue-400',
  medium: 'bg-amber-500/10 text-amber-400',
  high: 'bg-orange-500/10 text-orange-400',
  critical: 'bg-red-500/10 text-red-400',
}

const tierColors: Record<string, string> = {
  deterministic: 'bg-purple-500/10 text-purple-400',
  semantic: 'bg-teal-500/10 text-teal-400',
}

export function SeverityBadge({ severity }: { severity: string }) {
  const color = severityColors[severity] || 'bg-zinc-500/10 text-zinc-400'
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${color}`}>
      {severity}
    </span>
  )
}

export function TierBadge({ tier }: { tier: string }) {
  const color = tierColors[tier] || 'bg-zinc-500/10 text-zinc-400'
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${color}`}>
      {tier}
    </span>
  )
}
