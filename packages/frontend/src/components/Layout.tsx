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
        <header className="flex h-14 items-center justify-between border-b border-gray-200 bg-white px-6">
          <h1 className="text-lg font-semibold text-gray-900">Amini</h1>
          <div className="flex items-center gap-1 rounded-lg bg-gray-100 p-1">
            <button
              onClick={() => setViewMode('developer')}
              className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                viewMode === 'developer'
                  ? 'bg-white text-amini-700 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Code size={14} />
              Developer
            </button>
            <button
              onClick={() => setViewMode('compliance')}
              className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                viewMode === 'compliance'
                  ? 'bg-white text-amini-700 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
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
