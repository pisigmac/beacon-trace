import { useApi } from '../hooks/useApi'
import type { Trace } from '../types'
import { Search } from 'lucide-react'
import { useState } from 'react'

export default function Traces() {
  const { data: traces, loading } = useApi<Trace[]>('/api/v1/traces/?limit=100')
  const [filter, setFilter] = useState('')

  const filtered = (traces ?? []).filter((t) =>
    t.agent_id.toLowerCase().includes(filter.toLowerCase()) ||
    t.status.toLowerCase().includes(filter.toLowerCase())
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Traces</h1>
          <p className="text-sm text-textMuted mt-1">Browse all agent execution traces</p>
        </div>
        <div className="flex items-center gap-2 bg-surface border border-border rounded-card px-3 py-2">
          <Search className="w-4 h-4 text-textMuted" />
          <input
            type="text"
            placeholder="Filter by agent or status..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-transparent text-sm outline-none w-56 placeholder:text-textMuted"
          />
        </div>
      </div>

      <div className="bg-surface border border-border rounded-card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-textMuted">
              <th className="px-5 py-3 font-medium">Trace ID</th>
              <th className="px-5 py-3 font-medium">Agent</th>
              <th className="px-5 py-3 font-medium">Status</th>
              <th className="px-5 py-3 font-medium">Tokens</th>
              <th className="px-5 py-3 font-medium">Cost</th>
              <th className="px-5 py-3 font-medium">Duration</th>
              <th className="px-5 py-3 font-medium">Started</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {loading ? (
              <tr>
                <td colSpan={7} className="px-5 py-8 text-center text-textMuted">Loading traces...</td>
              </tr>
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-5 py-8 text-center text-textMuted">No traces found</td>
              </tr>
            ) : (
              filtered.map((trace) => (
                <tr key={trace.id} className="hover:bg-surfaceHover transition-colors">
                  <td className="px-5 py-3 font-mono text-xs">{trace.id.slice(0, 12)}...</td>
                  <td className="px-5 py-3">{trace.agent_id}</td>
                  <td className="px-5 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      trace.status === 'success' ? 'bg-success/10 text-success' :
                      trace.status === 'failure' ? 'bg-danger/10 text-danger' :
                      'bg-accent/10 text-accent'
                    }`}>
                      {trace.status}
                    </span>
                  </td>
                  <td className="px-5 py-3">{trace.total_tokens.toLocaleString()}</td>
                  <td className="px-5 py-3">${trace.cost_usd.toFixed(4)}</td>
                  <td className="px-5 py-3">{trace.duration_ms ? `${trace.duration_ms}ms` : '-'}</td>
                  <td className="px-5 py-3 text-textMuted">
                    {new Date(trace.started_at).toLocaleString()}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
