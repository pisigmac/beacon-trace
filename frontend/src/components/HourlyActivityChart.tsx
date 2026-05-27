import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface Props {
  data: { hour: string; count: number }[]
}

export default function HourlyActivityChart({ data }: Props) {
  return (
    <div className="bg-surface border border-border rounded-card p-5">
      <h3 className="font-medium text-sm mb-4">Hourly Activity (24h)</h3>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis dataKey="hour" stroke="#9CA3AF" fontSize={11} tickLine={false} />
          <YAxis stroke="#9CA3AF" fontSize={11} tickLine={false} />
          <Tooltip
            contentStyle={{ backgroundColor: '#242424', border: '1px solid #333', borderRadius: '6px', fontSize: '12px' }}
            itemStyle={{ color: '#F5F0EB' }}
          />
          <Bar dataKey="count" fill="#85C1E9" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
