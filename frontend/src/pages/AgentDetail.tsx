import { useParams } from 'react-router-dom'
import { useApi } from '../hooks/useApi'
import { ArrowLeft, Activity, Clock, DollarSign, Hash } from 'lucide-react'
import { Link } from 'react-router-dom'
import type { Agent, Trace } from '../types'

export default function AgentDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: agent } = useApi<Agent>(`/api/v1/agents/${id}`)
  const { data: traces } = useApi<Trace[]>(`/api/v1/agents/${id}/traces?limit=50`)
  const { data: _metrics } = useApi(`/api/v1/metrics/agent/${id}`)

  const statusColors = {
    healthy: 'bg-success',
    warning: 'bg-warning',
    critical: 'bg-danger',
    inactive: 'bg-textMuted',
  }

  return (
    <div className="space-y-6">
      <Link to="/" className="inline-flex items-center gap-2 text-sm text-textMuted hover:text-text transition-colors">
        <ArrowLeft className="w-4 h-4" />
        Back to Dashboard
      </Link>

      <div className="flex items-center gap-4">
        <div className={`w-3 h-3 rounded-full ${statusColors[agent?.status ?? 'inactive']}`} />
        <div>
          <h1 className="text-xl font-semibold">{agent?.name ?? id}</h1>
          <p className="text-sm text-textMuted">{agent?.framework} · {agent?.model}</p>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-surface border border-border rounded-card p-4">
          <div className="flex items-center gap-2 text-textMuted mb-2">
            <Hash className="w-4 h-4" />
            <span className="text-xs uppercase font-medium">Total Runs</span>
          </div>
          <p className="text-2xl font-semibold">{agent?.total_runs ?? 0}</p>
        </div>
        <div className="bg-surface border border-border rounded-card p-4">
          <div className="flex items-center gap-2 text-textMuted mb-2">
            <Activity className="w-4 h-4" />
            <span className="text-xs uppercase font-medium">Success Rate</span>
          </div>
          <p className="text-2xl font-semibold">{(agent?.success_rate ?? 0).toFixed(1)}%</p>
        </div>
        <div className="bg-surface border border-border rounded-card p-4">
          <div className="flex items-center gap-2 text-textMuted mb-2">
            <Clock className="w-4 h-4" />
            <span className="text-xs uppercase font-medium">Avg Latency</span>
          </div>
          <p className="text-2xl font-semibold">{(agent?.avg_latency_ms ?? 0).toFixed(0)}ms</p>
        </div>
        <div className="bg-surface border border-border rounded-card p-4">
          <div className="flex items-center gap-2 text-textMuted mb-2">
            <DollarSign className="w-4 h-4" />
            <span className="text-xs uppercase font-medium">Total Cost</span>
          </div>
          <p className="text-2xl font-semibold">${(agent?.total_cost_usd ?? 0).toFixed(2)}</p>
        </div>
      </div>

      <div className="bg-surface border border-border rounded-card">
        <div className="px-5 py-4 border-b border-border">
          <h3 className="font-medium text-sm">Recent Traces</h3>
        </div>
        <div className="divide-y divide-border">
          {(traces ?? []).map((trace) => (
            <div key={trace.id} className="px-5 py-3 flex items-center justify-between hover:bg-surfaceHover transition-colors">
              <div>
                <p className="text-sm font-mono">{trace.id.slice(0, 8)}...</p>
                <p className="text-xs text-textMuted mt-0.5">
                  {trace.total_tokens.toLocaleString()} tokens · {trace.duration_ms ? `${trace.duration_ms}ms` : 'running'}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  trace.status === 'success' ? 'bg-success/10 text-success' :
                  trace.status === 'failure' ? 'bg-danger/10 text-danger' :
                  'bg-accent/10 text-accent'
                }`}>
                  {trace.status}
                </span>
                <span className="text-sm font-medium">${trace.cost_usd.toFixed(4)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
