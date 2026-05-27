import { useApi } from '../hooks/useApi'
import { useWebSocket } from '../hooks/useWebSocket'
import { useEffect, useState } from 'react'
import StatCard from '../components/StatCard'
import AgentGrid from '../components/AgentGrid'
import ActivityFeed from '../components/ActivityFeed'
import AlertPanel from '../components/AlertPanel'
import CostTrendChart from '../components/CostTrendChart'
import HourlyActivityChart from '../components/HourlyActivityChart'
import type { MetricsSummary, Agent, Trace, Alert } from '../types'
import { Activity, TrendingUp, AlertTriangle, Wifi, WifiOff } from 'lucide-react'

export default function Dashboard() {
  const { data: metricsData } = useApi<MetricsSummary>('/api/v1/metrics/summary')
  const { data: agentsData } = useApi<Agent[]>('/api/v1/agents/')
  const { data: tracesData } = useApi<Trace[]>('/api/v1/traces/?limit=20')
  const { data: alertsData } = useApi<Alert[]>('/api/v1/alerts/?resolved=false')

  const { connected, lastEvent } = useWebSocket()

  const [agents, setAgents] = useState<Agent[]>([])
  const [traces, setTraces] = useState<Trace[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [liveMetrics, setLiveMetrics] = useState<MetricsSummary | null>(null)

  // Initialize from API
  useEffect(() => { if (agentsData) setAgents(agentsData) }, [agentsData])
  useEffect(() => { if (tracesData) setTraces(tracesData) }, [tracesData])
  useEffect(() => { if (alertsData) setAlerts(alertsData) }, [alertsData])
  useEffect(() => { if (metricsData) setLiveMetrics(metricsData) }, [metricsData])

  // Handle WebSocket events
  useEffect(() => {
    if (!lastEvent) return

    switch (lastEvent.type) {
      case 'trace_started': {
        const newTrace: Trace = {
          id: lastEvent.data.id,
          agent_id: lastEvent.data.agent_id,
          status: 'running',
          started_at: new Date().toISOString(),
          ended_at: null,
          duration_ms: null,
          total_tokens: 0,
          cost_usd: 0,
          error_message: null,
        }
        setTraces((prev) => [newTrace, ...prev].slice(0, 20))
        setLiveMetrics((prev) => prev ? {
          ...prev,
          total_traces_24h: prev.total_traces_24h + 1,
        } : prev)
        break
      }
      case 'trace_updated': {
        setTraces((prev) =>
          prev.map((t) =>
            t.id === lastEvent.data.id ? { ...t, status: lastEvent.data.status } : t
          )
        )
        break
      }
      case 'alert_created': {
        const newAlert: Alert = {
          id: lastEvent.data.id,
          agent_id: lastEvent.data.agent_id,
          type: lastEvent.data.type,
          severity: lastEvent.data.severity,
          message: lastEvent.data.message,
          created_at: new Date().toISOString(),
          resolved: false,
        }
        setAlerts((prev) => [newAlert, ...prev])
        setLiveMetrics((prev) => prev ? {
          ...prev,
          active_alerts: prev.active_alerts + 1,
        } : prev)
        break
      }
    }
  }, [lastEvent])

  const metrics = liveMetrics ?? metricsData

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold">Dashboard</h1>
          <p className="text-sm text-textMuted mt-1">Real-time observability for your AI agents</p>
        </div>
        <div className={`flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border ${
          connected
            ? 'border-success/30 text-success bg-success/10'
            : 'border-textMuted/30 text-textMuted bg-textMuted/10'
        }`}>
          {connected ? <Wifi className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
          {connected ? 'Live' : 'Reconnecting...'}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Active Agents"
          value={metrics?.total_agents ?? 0}
          icon={<Activity className="w-5 h-5" />}
        />
        <StatCard
          title="24h Traces"
          value={metrics?.total_traces_24h ?? 0}
          subtitle={`${(metrics?.total_cost_24h ?? 0).toFixed(2)} spent`}
          icon={<TrendingUp className="w-5 h-5" />}
        />
        <StatCard
          title="Success Rate"
          value={`${(metrics?.avg_success_rate ?? 0).toFixed(1)}%`}
          trend={metrics && metrics.avg_success_rate > 95 ? 'up' : 'down'}
          icon={<TrendingUp className="w-5 h-5" />}
        />
        <StatCard
          title="Active Alerts"
          value={metrics?.active_alerts ?? 0}
          trend={metrics && metrics.active_alerts > 0 ? 'down' : 'up'}
          icon={<AlertTriangle className="w-5 h-5" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <AgentGrid agents={agents} />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <CostTrendChart data={metrics?.cost_trend ?? []} />
            <HourlyActivityChart data={metrics?.hourly_activity ?? []} />
          </div>
        </div>
        <div className="space-y-6">
          <AlertPanel alerts={alerts} />
          <ActivityFeed traces={traces} />
        </div>
      </div>
    </div>
  )
}
