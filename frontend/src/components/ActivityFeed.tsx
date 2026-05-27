import { Clock, CheckCircle2, XCircle, Loader2 } from 'lucide-react'
import type { Trace } from '../types'

const statusIcons = {
  success: { icon: CheckCircle2, color: 'text-success' },
  failure: { icon: XCircle, color: 'text-danger' },
  running: { icon: Loader2, color: 'text-accent' },
}

export default function ActivityFeed({ traces }: { traces: Trace[] }) {
  return (
    <div className="bg-surface border border-border rounded-card">
      <div className="px-5 py-4 border-b border-border">
        <h3 className="font-medium text-sm">Recent Activity</h3>
      </div>
      <div className="divide-y divide-border">
        {traces.slice(0, 10).map((trace) => {
          const cfg = statusIcons[trace.status as keyof typeof statusIcons] || statusIcons.running
          const Icon = cfg.icon
          const time = new Date(trace.started_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          return (
            <div key={trace.id} className="px-5 py-3 flex items-center gap-3 hover:bg-surfaceHover transition-colors">
              <Icon className={`w-4 h-4 ${cfg.color} ${trace.status === 'running' ? 'animate-spin' : ''}`} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{trace.agent_id}</p>
                <p className="text-xs text-textMuted">{trace.total_tokens.toLocaleString()} tokens · ${trace.cost_usd.toFixed(4)}</p>
              </div>
              <div className="flex items-center gap-1 text-xs text-textMuted">
                <Clock className="w-3 h-3" />
                {time}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
