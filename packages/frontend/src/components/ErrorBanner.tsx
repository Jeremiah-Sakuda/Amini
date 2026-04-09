import { AlertTriangle } from 'lucide-react'

export function ErrorBanner({ message }: { message?: string }) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4 flex items-center gap-3">
      <AlertTriangle size={20} className="text-red-600 flex-shrink-0" />
      <div className="text-sm text-red-800">
        <p className="font-medium">Something went wrong</p>
        {message && <p className="mt-1 text-red-600">{message}</p>}
      </div>
    </div>
  )
}
