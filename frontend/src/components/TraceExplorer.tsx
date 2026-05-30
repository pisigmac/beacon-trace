import React, { useState, useEffect } from 'react';
import { Trace, Step } from '../types';

export const TraceExplorer: React.FC = () => {
  const [traces, setTraces] = useState<Trace[]>([]);
  const [selectedTrace, setSelectedTrace] = useState<Trace | null>(null);
  const [filters, setFilters] = useState({
    parent_trace_id: '',
    retry_count_min: 0,
    first_failure_step: undefined as number | undefined
  });

  useEffect(() => {
    fetchTraces();
  }, [filters]);

  const fetchTraces = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.parent_trace_id) params.append('parent_trace_id', filters.parent_trace_id);
      if (filters.retry_count_min > 0) params.append('retry_count_min', filters.retry_count_min.toString());
      if (filters.first_failure_step !== undefined) params.append('first_failure_step', filters.first_failure_step.toString());

      const res = await fetch(`http://localhost:8000/api/v1/traces?${params}`);
      const data = await res.json();
      setTraces(data);
    } catch (err) {
      console.error('Failed to fetch traces:', err);
    }
  };

  const getStepIndicator = (step: Step, failureStep?: number) => {
    if (failureStep === undefined) return '✓';
    if (step.step_number < failureStep) return '✅';
    if (step.step_number === failureStep) return '❌';
    return '⊘';
  };

  return (
    <div className="bg-surface border border-border rounded-card p-5">
      <h3 className="font-medium text-sm mb-4">Trace Explorer</h3>

      <div className="mb-4 grid grid-cols-3 gap-2">
        <input
          type="text"
          placeholder="Parent trace ID"
          value={filters.parent_trace_id}
          onChange={(e) => setFilters({ ...filters, parent_trace_id: e.target.value })}
          className="px-2 py-1 bg-surface border border-border rounded text-xs"
        />
        <input
          type="number"
          placeholder="Min retries"
          value={filters.retry_count_min}
          onChange={(e) => setFilters({ ...filters, retry_count_min: parseInt(e.target.value) || 0 })}
          className="px-2 py-1 bg-surface border border-border rounded text-xs"
        />
        <input
          type="number"
          placeholder="Failure step"
          value={filters.first_failure_step || ''}
          onChange={(e) => setFilters({ ...filters, first_failure_step: e.target.value ? parseInt(e.target.value) : undefined })}
          className="px-2 py-1 bg-surface border border-border rounded text-xs"
        />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead className="bg-surface border-b border-border">
            <tr>
              <th className="px-2 py-1 text-left">Trace ID</th>
              <th className="px-2 py-1 text-left">Agent</th>
              <th className="px-2 py-1 text-left">Status</th>
              <th className="px-2 py-1 text-left">Duration</th>
              <th className="px-2 py-1 text-left">Cost</th>
              <th className="px-2 py-1 text-left">Retries</th>
              <th className="px-2 py-1 text-left">Failure</th>
              <th className="px-2 py-1 text-left">Parent</th>
            </tr>
          </thead>
          <tbody>
            {traces.map((trace) => (
              <tr
                key={trace.id}
                onClick={() => setSelectedTrace(trace)}
                className="border-b border-border hover:bg-surface/50 cursor-pointer"
              >
                <td className="px-2 py-1 font-mono text-textMuted">{trace.id.slice(0, 8)}</td>
                <td className="px-2 py-1">{trace.agent_id}</td>
                <td className="px-2 py-1">
                  <span style={{
                    backgroundColor: trace.status === 'success' ? 'rgba(34, 197, 94, 0.2)' : trace.status === 'failure' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(234, 179, 8, 0.2)',
                    color: trace.status === 'success' ? '#22c55e' : trace.status === 'failure' ? '#ef4444' : '#eab308',
                    padding: '2px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: 'bold'
                  }}>
                    {trace.status}
                  </span>
                </td>
                <td className="px-2 py-1">{trace.duration_ms ? `${trace.duration_ms}ms` : '-'}</td>
                <td className="px-2 py-1">${trace.cost_usd.toFixed(4)}</td>
                <td className="px-2 py-1">{trace.retry_count}</td>
                <td className="px-2 py-1">{trace.first_failure_step_number || '-'}</td>
                <td className="px-2 py-1 font-mono text-textMuted">{trace.parent_trace_id?.slice(0, 8) || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedTrace && (
        <div className="mt-4 p-3 bg-surface border border-border rounded">
          <h4 className="font-medium text-sm mb-2">Trace: {selectedTrace.id.slice(0, 8)}</h4>
          
          {selectedTrace.first_failure_step_number && (
            <div className="mb-3 p-2 bg-error/10 border border-error/30 rounded text-xs">
              <p className="font-semibold text-error">Failed at Step {selectedTrace.first_failure_step_number}</p>
              <p className="text-textMuted">{selectedTrace.first_failure_reason}</p>
            </div>
          )}

          <div className="space-y-1">
            {selectedTrace.steps?.map((step) => (
              <div key={step.step_number} className="flex items-center gap-2 p-1 text-xs">
                <span>{getStepIndicator(step, selectedTrace.first_failure_step_number)}</span>
                <span className="font-medium">{step.type}</span>
                {step.tool_name && <span className="text-textMuted">({step.tool_name})</span>}
                <span className="text-textMuted ml-auto">{step.latency_ms}ms</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
