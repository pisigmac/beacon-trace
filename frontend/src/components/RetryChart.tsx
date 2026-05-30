import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const RetryChart: React.FC = () => {
  const [data, setData] = useState<any[]>([]);
  const [avgCost, setAvgCost] = useState(0);

  useEffect(() => {
    fetchRetryDistribution();
  }, []);

  const fetchRetryDistribution = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/metrics/retry-distribution');
      const result = await res.json();
      setData(result.distribution);
      setAvgCost(result.avg_cost_with_retries);
    } catch (err) {
      console.error('Failed to fetch retry distribution:', err);
    }
  };

  return (
    <div className="bg-surface border border-border rounded-card p-5">
      <h3 className="font-medium text-sm mb-4">Retry Distribution</h3>
      <p className="text-xs text-textMuted mb-4">Avg cost: ${avgCost.toFixed(4)}</p>
      
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis dataKey="retry_count" stroke="#9CA3AF" fontSize={11} tickLine={false} label={{ value: 'Retry Count', position: 'insideBottomRight', offset: -5, fill: '#9CA3AF', fontSize: 11 }} />
          <YAxis stroke="#9CA3AF" fontSize={11} tickLine={false} allowDecimals={false} />
          <Tooltip
            contentStyle={{ backgroundColor: '#242424', border: '1px solid #333', borderRadius: '6px', fontSize: '12px' }}
            itemStyle={{ color: '#F5F0EB' }}
            formatter={(value: number) => [value, 'Traces']}
          />
          <Bar dataKey="trace_count" fill="#60A5FA" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
