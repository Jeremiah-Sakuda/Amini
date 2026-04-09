import { AlertTriangle } from 'lucide-react'

export function ErrorBanner({ message }: { message?: string }) {
  return (
    <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-4 flex items-center gap-3">
      <AlertTriangle size={20} className="text-red-400 flex-shrink-0" />
      <div className="text-sm text-red-300">
        <p className="font-medium">Something went wrong</p>
        {message && <p className="mt-1 text-red-400">{message}</p>}
      </div>
    </div>
  )
}
