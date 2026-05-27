import { Link } from 'react-router-dom'
import { Activity, AlertTriangle, AlertCircle, PauseCircle } from 'lucide-react'
import type { Agent } from '../types'

const statusConfig = {
  healthy: { icon: Activity, color: 'text-success', bg: 'bg-success/10', border: 'border-success/20' },
  warning: { icon: AlertTriangle, color: 'text-warning', bg: 'bg-warning/10', border: 'border-warning/20' },
  critical: { icon: AlertCircle, color: 'text-danger', bg: 'bg-danger/10', border: 'border-danger/20' },
  inactive: { icon: PauseCircle, color: 'text-textMuted', bg: 'bg-textMuted/10', border: 'border-textMuted/20' },
}

export default function AgentGrid({ agents }: { agents: Agent[] }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {agents.map((agent) => {
        const cfg = statusConfig[agent.status]
        const Icon = cfg.icon
        return (
          <Link
            key={agent.id}
            to={`/agents/${agent.id}`}
            className={`bg-surface border ${cfg.border} rounded-card p-5 hover:bg-surfaceHover transition-colors group`}
          >
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${cfg.bg.replace('/10', '')}`} />
                  <h3 className="font-medium text-sm">{agent.name}</h3>
                </div>
                <p className="text-xs text-textMuted mt-1">{agent.framework} · {agent.model}</p>
              </div>
              <Icon className={`w-4 h-4 ${cfg.color}`} />
            </div>
            <div className="grid grid-cols-3 gap-3 mt-4 pt-4 border-t border-border">
              <div>
                <p className="text-lg font-semibold">{agent.total_runs}</p>
                <p className="text-[10px] text-textMuted uppercase">Runs</p>
              </div>
              <div>
                <p className="text-lg font-semibold">{agent.success_rate.toFixed(0)}%</p>
                <p className="text-[10px] text-textMuted uppercase">Success</p>
              </div>
              <div>
                <p className="text-lg font-semibold">${agent.total_cost_usd.toFixed(2)}</p>
                <p className="text-[10px] text-textMuted uppercase">Cost</p>
              </div>
            </div>
          </Link>
        )
      })}
    </div>
  )
}
