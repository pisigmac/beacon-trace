import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface Props {
  data: { day: string; cost_usd: number }[]
}

export default function CostTrendChart({ data }: Props) {
  return (
    <div className="bg-surface border border-border rounded-card p-5">
      <h3 className="font-medium text-sm mb-4">Cost Trend (7 Days)</h3>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#E8A87C" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#E8A87C" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis dataKey="day" stroke="#9CA3AF" fontSize={11} tickLine={false} />
          <YAxis stroke="#9CA3AF" fontSize={11} tickLine={false} tickFormatter={(v) => `$${v.toFixed(2)}`} />
          <Tooltip
            contentStyle={{ backgroundColor: '#242424', border: '1px solid #333', borderRadius: '6px', fontSize: '12px' }}
            itemStyle={{ color: '#F5F0EB' }}
            formatter={(value: number) => [`$${value.toFixed(3)}`, 'Cost']}
          />
          <Area type="monotone" dataKey="cost_usd" stroke="#E8A87C" strokeWidth={2} fill="url(#costGradient)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
