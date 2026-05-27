import { ReactNode } from 'react'

interface StatCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: ReactNode
  trend?: 'up' | 'down' | 'neutral'
}

export default function StatCard({ title, value, subtitle, icon, trend }: StatCardProps) {
  const trendColor = trend === 'up' ? 'text-success' : trend === 'down' ? 'text-danger' : 'text-textMuted'
  return (
    <div className="bg-surface border border-border rounded-card p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-textMuted uppercase tracking-wider">{title}</p>
          <p className="text-2xl font-semibold mt-1.5">{value}</p>
          {subtitle && <p className={`text-xs mt-1 ${trendColor}`}>{subtitle}</p>}
        </div>
        <div className="text-textMuted">{icon}</div>
      </div>
    </div>
  )
}
