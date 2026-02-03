import { Skeleton } from '@/components/ui/Skeleton'

interface StatsCardProps {
  title: string
  value: string | number
  change?: number
  changeLabel?: string
  icon: React.ReactNode
  trend?: 'up' | 'down' | 'neutral'
  isLoading?: boolean
}

export default function StatsCard({
  title,
  value,
  change,
  changeLabel,
  icon,
  trend = 'neutral',
  isLoading = false,
}: StatsCardProps) {
  const trendColors = {
    up: 'text-crypto-gain',
    down: 'text-crypto-loss',
    neutral: 'text-crypto-text-secondary',
  }

  const trendBgColors = {
    up: 'bg-crypto-gain/20',
    down: 'bg-crypto-loss/20',
    neutral: 'bg-crypto-accent/20',
  }

  return (
    <div className="card">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="stat-label">{title}</p>
          {isLoading ? (
            <div className="mt-2 space-y-2">
              <Skeleton className="h-8 w-24" />
              <Skeleton className="h-4 w-16" />
            </div>
          ) : (
            <>
              <p className="stat-value mt-1">{value}</p>
              {change !== undefined && (
                <div className="flex items-center gap-1 mt-2">
                  <span className={trendColors[trend]}>
                    {trend === 'up' && '+'}
                    {typeof change === 'number' ? change.toFixed(2) : change}%
                  </span>
                  {changeLabel && (
                    <span className="text-xs text-crypto-text-muted">{changeLabel}</span>
                  )}
                </div>
              )}
            </>
          )}
        </div>
        <div className={`p-3 rounded-lg ${trendBgColors[trend]}`}>
          <div className={trendColors[trend]}>{icon}</div>
        </div>
      </div>
    </div>
  )
}
