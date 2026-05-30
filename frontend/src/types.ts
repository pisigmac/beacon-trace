export interface Agent {
  id: string;
  name: string;
  framework: string | null;
  model: string | null;
  created_at: string;
  last_seen: string | null;
  total_runs: number;
  success_rate: number;
  avg_latency_ms: number;
  total_cost_usd: number;
  status: 'healthy' | 'warning' | 'critical' | 'inactive';
}

export interface Trace {
  id: string;
  agent_id: string;
  status: string;
  started_at: string;
  ended_at: string | null;
  duration_ms: number | null;
  total_tokens: number;
  cost_usd: number;
  error_message: string | null;
  parent_trace_id?: string;
  first_failure_step_number?: number;
  first_failure_reason?: string;
  retry_count: number;
  steps?: Step[];
}

export interface Step {
  step_number: number;
  type: string;
  timestamp: string;
  duration_ms: number;
  input_tokens: number;
  output_tokens: number;
  cost_usd: number;
  tool_name?: string;
  model?: string;
  latency_ms: number;
  status: string;
  error?: string;
  tool_status: string;
  tool_response_code?: number;
  tool_error?: string;
  retry_count: number;
  retry_history?: any[];
}

export interface Alert {
  id: string;
  agent_id: string | null;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  message: string;
  created_at: string;
  resolved: boolean;
}

export interface MetricsSummary {
  total_agents: number;
  total_traces_24h: number;
  total_cost_24h: number;
  avg_success_rate: number;
  active_alerts: number;
  top_agents_by_cost: { agent_id: string; cost_usd: number }[];
  hourly_activity: { hour: string; count: number }[];
  cost_trend: { day: string; cost_usd: number }[];
}
