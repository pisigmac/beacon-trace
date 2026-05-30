import React, { useState, useEffect } from 'react';
import { Trace } from '../types';

interface TraceNode extends Trace {
  children?: TraceNode[];
}

export const TraceTree: React.FC = () => {
  const [rootTraces, setRootTraces] = useState<TraceNode[]>([]);
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchRootTraces();
  }, []);

  const fetchRootTraces = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/traces?parent_trace_id=');
      const traces = await res.json();
      const roots = traces.filter((t: Trace) => !t.parent_trace_id);
      
      // Fetch full tree for each root
      const treesWithChildren = await Promise.all(
        roots.map(async (root: Trace) => {
          const treeRes = await fetch(`http://localhost:8000/api/v1/traces/${root.id}/tree`);
          return treeRes.json();
        })
      );
      
      setRootTraces(treesWithChildren);
    } catch (err) {
      console.error('Failed to fetch trace tree:', err);
    }
  };

  const toggleExpand = (id: string) => {
    const newExpanded = new Set(expandedIds);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedIds(newExpanded);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'text-success';
      case 'failure': return 'text-error';
      case 'running': return 'text-warning';
      default: return 'text-textMuted';
    }
  };

  const renderNode = (node: TraceNode, depth: number = 0) => {
    const hasChildren = node.children && node.children.length > 0;
    const isExpanded = expandedIds.has(node.id);

    return (
      <div key={node.id} style={{ marginLeft: `${depth * 20}px` }}>
        <div className="flex items-center gap-2 py-2 hover:bg-surface/50 rounded px-2">
          {hasChildren && (
            <button
              onClick={() => toggleExpand(node.id)}
              className="w-5 h-5 flex items-center justify-center text-textMuted hover:bg-border rounded"
            >
              {isExpanded ? '▼' : '▶'}
            </button>
          )}
          {!hasChildren && <div className="w-5" />}
          
          <span className={`font-mono text-xs ${getStatusColor(node.status)}`}>
            {node.id.slice(0, 8)}
          </span>
          <span className="text-sm font-semibold text-text">{node.agent_id}</span>
          <span style={{
            backgroundColor: node.status === 'success' ? 'rgba(34, 197, 94, 0.2)' : node.status === 'failure' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(234, 179, 8, 0.2)',
            color: node.status === 'success' ? '#22c55e' : node.status === 'failure' ? '#ef4444' : '#eab308',
            padding: '2px 8px',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: 'bold'
          }}>
            {node.status}
          </span>
          <span className="text-xs text-textMuted">
            ${node.cost_usd.toFixed(4)} | {node.retry_count} retries
          </span>
        </div>

        {hasChildren && isExpanded && (
          <div>
            {node.children!.map((child) => renderNode(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="bg-surface border border-border rounded-card p-5">
      <h3 className="font-medium text-sm mb-4">Trace Hierarchy</h3>
      <div className="space-y-1 text-sm">
        {rootTraces.map((trace) => renderNode(trace))}
      </div>
    </div>
  );
};
