import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { Code, Shield } from 'lucide-react'

export type ViewMode = 'developer' | 'compliance'

export function Layout() {
  const [viewMode, setViewMode] = useState<ViewMode>('developer')

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex h-14 items-center justify-between border-b border-zinc-800 bg-zinc-950 px-6">
          <h1 className="text-lg font-semibold text-zinc-100">Amini</h1>
          <div className="flex items-center gap-1 rounded-lg bg-zinc-800 p-1">
            <button
              onClick={() => setViewMode('developer')}
              className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                viewMode === 'developer'
                  ? 'bg-zinc-700 text-zinc-100'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <Code size={14} />
              Developer
            </button>
            <button
              onClick={() => setViewMode('compliance')}
              className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                viewMode === 'compliance'
                  ? 'bg-zinc-700 text-zinc-100'
                  : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <Shield size={14} />
              Compliance
            </button>
          </div>
        </header>
        <main className="flex-1 overflow-auto p-6">
          <Outlet context={{ viewMode }} />
        </main>
      </div>
    </div>
  )
}
