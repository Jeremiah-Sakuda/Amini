import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  List,
  ShieldCheck,
  AlertTriangle,
  Bot,
  BookOpen,
  AlertOctagon,
  FileText,
  Settings,
} from 'lucide-react'

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/registry', icon: Bot, label: 'Agent Registry' },
  { to: '/sessions', icon: List, label: 'Sessions' },
  { to: '/policies', icon: ShieldCheck, label: 'Policies' },
  { to: '/regulations', icon: BookOpen, label: 'Regulations' },
  { to: '/violations', icon: AlertTriangle, label: 'Violations' },
  { to: '/incidents', icon: AlertOctagon, label: 'Incidents' },
  { to: '/reports', icon: FileText, label: 'Audit Reports' },
  { to: '/settings', icon: Settings, label: 'Settings' },
]

export function Sidebar() {
  return (
    <aside className="flex w-56 flex-col border-r border-zinc-800 bg-zinc-950">
      <div className="flex h-14 items-center border-b border-zinc-800 px-4">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-indigo-600 flex items-center justify-center">
            <span className="text-sm font-bold text-white">A</span>
          </div>
          <div>
            <span className="text-sm font-semibold text-zinc-100">Amini</span>
            <span className="ml-1.5 rounded bg-indigo-500/10 px-1 py-0.5 text-[10px] font-medium text-indigo-400">
              v2
            </span>
          </div>
        </div>
      </div>
      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-indigo-500/10 text-indigo-400'
                  : 'text-zinc-500 hover:bg-zinc-800/50 hover:text-zinc-200'
              }`
            }
          >
            <item.icon size={16} />
            {item.label}
          </NavLink>
        ))}
      </nav>
      <div className="border-t border-zinc-800 p-3">
        <p className="text-[10px] text-zinc-600 text-center">Compliance Infrastructure</p>
      </div>
    </aside>
  )
}
