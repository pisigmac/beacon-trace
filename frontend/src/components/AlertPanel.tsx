import { AlertTriangle, AlertCircle, Info, X } from 'lucide-react'
import type { Alert } from '../types'

const severityConfig = {
  critical: { icon: AlertTriangle, color: 'text-danger', bg: 'bg-danger/10', border: 'border-danger/20' },
  high: { icon: AlertCircle, color: 'text-warning', bg: 'bg-warning/10', border: 'border-warning/20' },
  medium: { icon: Info, color: 'text-accent', bg: 'bg-accent/10', border: 'border-accent/20' },
  low: { icon: Info, color: 'text-textMuted', bg: 'bg-textMuted/10', border: 'border-textMuted/20' },
}

export default function AlertPanel({ alerts }: { alerts: Alert[] }) {
  const unresolved = alerts.filter((a) => !a.resolved)
  return (
    <div className="bg-surface border border-border rounded-card">
      <div className="px-5 py-4 border-b border-border flex items-center justify-between">
        <h3 className="font-medium text-sm">Active Alerts</h3>
        {unresolved.length > 0 && (
          <span className="text-xs bg-danger/10 text-danger px-2 py-0.5 rounded-full font-medium">
            {unresolved.length}
          </span>
        )}
      </div>
      <div className="divide-y divide-border max-h-80 overflow-auto">
        {unresolved.length === 0 ? (
          <div className="px-5 py-8 text-center text-sm text-textMuted">
            All clear. No active alerts.
          </div>
        ) : (
          unresolved.map((alert) => {
            const cfg = severityConfig[alert.severity]
            const Icon = cfg.icon
            return (
              <div key={alert.id} className={`px-5 py-3 ${cfg.bg} border-l-2 ${cfg.border.replace('border-', 'border-l-')}`}>
                <div className="flex items-start gap-2.5">
                  <Icon className={`w-4 h-4 ${cfg.color} mt-0.5`} />
                  <div className="flex-1">
                    <p className="text-sm font-medium">{alert.type.replace(/_/g, ' ')}</p>
                    <p className="text-xs text-textMuted mt-0.5">{alert.message}</p>
                    <p className="text-[10px] text-textMuted mt-1.5">
                      {new Date(alert.created_at).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}
