const severityColors: Record<string, string> = {
  low: 'bg-blue-100 text-blue-700',
  medium: 'bg-yellow-100 text-yellow-700',
  high: 'bg-orange-100 text-orange-700',
  critical: 'bg-red-100 text-red-700',
}

const tierColors: Record<string, string> = {
  deterministic: 'bg-purple-100 text-purple-700',
  semantic: 'bg-teal-100 text-teal-700',
}

export function SeverityBadge({ severity }: { severity: string }) {
  const color = severityColors[severity] || 'bg-gray-100 text-gray-700'
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${color}`}>
      {severity}
    </span>
  )
}

export function TierBadge({ tier }: { tier: string }) {
  const color = tierColors[tier] || 'bg-gray-100 text-gray-700'
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${color}`}>
      {tier}
    </span>
  )
}
