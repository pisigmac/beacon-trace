import { Link, useLocation } from 'react-router-dom'
import { Activity, Radio, FileText, Zap } from 'lucide-react'
import { ReactNode } from 'react'

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation()
  const nav = [
    { path: '/', label: 'Dashboard', icon: Activity },
    { path: '/traces', label: 'Traces', icon: FileText },
  ]

  return (
    <div className="min-h-screen flex">
      <aside className="w-56 bg-surface border-r border-border flex flex-col">
        <div className="p-5 flex items-center gap-2.5">
          <Zap className="w-5 h-5 text-primary" />
          <span className="font-semibold text-lg tracking-tight">Beacon</span>
        </div>
        <nav className="flex-1 px-3 py-2 space-y-0.5">
          {nav.map((item) => {
            const active = location.pathname === item.path
            const Icon = item.icon
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-card text-sm font-medium transition-colors ${
                  active
                    ? 'bg-surfaceHover text-text'
                    : 'text-textMuted hover:text-text hover:bg-surfaceHover'
                }`}
              >
                <Icon className="w-4 h-4" />
                {item.label}
              </Link>
            )
          })}
        </nav>
        <div className="p-4 border-t border-border">
          <div className="flex items-center gap-2 text-xs text-textMuted">
            <Radio className="w-3 h-3 text-success" />
            <span>Collector active</span>
          </div>
        </div>
      </aside>
      <main className="flex-1 overflow-auto">
        <div className="max-w-7xl mx-auto p-6">
          {children}
        </div>
      </main>
    </div>
  )
}
