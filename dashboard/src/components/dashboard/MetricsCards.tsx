import { useQuery } from '@tanstack/react-query'
import { metricsService } from '@/services/metrics.service'
import { Skeleton } from '@/components/ui/Skeleton'

interface MetricCard {
  title: string
  value: string | number
  change?: number
  changeLabel?: string
  icon: React.ReactNode
  color: 'accent' | 'gain' | 'loss' | 'purple' | 'blue'
  trend?: 'up' | 'down' | 'neutral'
  isLoading: boolean
  isError: boolean
}

export default function MetricsCards() {
  const { data: marketOverview, isLoading: loadingMarket, isError: errorMarket } = useQuery({
    queryKey: ['marketOverview'],
    queryFn: metricsService.getMarketOverview,
    refetchInterval: 60000,
  })

  const { data: alertMetrics, isLoading: loadingAlerts, isError: errorAlerts } = useQuery({
    queryKey: ['alertMetrics'],
    queryFn: metricsService.getAlertMetrics,
    refetchInterval: 300000, // Sync cada 5 minutos
  })

  const { data: portfolioMetrics, isLoading: loadingPortfolio, isError: errorPortfolio } = useQuery({
    queryKey: ['portfolioMetrics'],
    queryFn: metricsService.getPortfolioMetrics,
    refetchInterval: 300000, // Sync cada 5 minutos
  })

  const metrics: MetricCard[] = [
    {
      title: 'Total Market Cap',
      value: `$${((marketOverview?.totalMarketCap || 0) / 1e12).toFixed(2)}T`,
      change: marketOverview?.marketCapChange24h,
      changeLabel: '24h',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'accent',
      trend: (marketOverview?.marketCapChange24h || 0) >= 0 ? 'up' : 'down',
      isLoading: loadingMarket,
      isError: errorMarket,
    },
    {
      title: 'Portfolio Value',
      value: `$${(portfolioMetrics?.totalValue || 0).toLocaleString()}`,
      change: portfolioMetrics?.pnlPercentage,
      changeLabel: 'P&L',
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: (portfolioMetrics?.pnlPercentage || 0) >= 0 ? 'gain' : 'loss',
      trend: (portfolioMetrics?.pnlPercentage || 0) >= 0 ? 'up' : 'down',
      isLoading: loadingPortfolio,
      isError: errorPortfolio,
    },
    {
      title: 'Active Alerts',
      value: alertMetrics?.active || 0,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
      ),
      color: 'purple',
      trend: 'neutral',
      isLoading: loadingAlerts,
      isError: errorAlerts,
    },
    {
      title: 'Triggered Today',
      value: alertMetrics?.triggeredToday || 0,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'blue',
      trend: 'up',
      isLoading: loadingAlerts,
      isError: errorAlerts,
    },
    {
      title: 'BTC Dominance',
      value: `${(marketOverview?.btcDominance || 0).toFixed(1)}%`,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" />
        </svg>
      ),
      color: 'accent',
      trend: 'neutral',
      isLoading: loadingMarket,
      isError: errorMarket,
    },
    {
      title: '24h Volume',
      value: `$${((marketOverview?.totalVolume24h || 0) / 1e9).toFixed(1)}B`,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      color: 'gain',
      trend: 'neutral',
      isLoading: loadingMarket,
      isError: errorMarket,
    },
  ]

  const colorClasses = {
    accent: 'from-crypto-accent/20 to-crypto-accent/5 text-crypto-accent',
    gain: 'from-crypto-gain/20 to-crypto-gain/5 text-crypto-gain',
    loss: 'from-crypto-loss/20 to-crypto-loss/5 text-crypto-loss',
    purple: 'from-crypto-purple/20 to-crypto-purple/5 text-crypto-purple',
    blue: 'from-crypto-blue/20 to-crypto-blue/5 text-crypto-blue',
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {metrics.map((metric) => (
        <div
          key={metric.title}
          className={`relative overflow-hidden rounded-xl bg-gradient-to-br ${colorClasses[metric.color]} border border-crypto-border p-4 transition-all duration-300 hover:scale-[1.02] hover:shadow-crypto`}
        >
          <div className="flex items-start justify-between mb-3">
            <div className={`p-2 rounded-lg bg-crypto-bg-tertiary`}>
              {metric.icon}
            </div>
            {metric.isLoading ? (
              <Skeleton className="w-12 h-5 rounded" />
            ) : metric.isError ? (
              <span className="text-[10px] text-crypto-loss opacity-50">Error</span>
            ) : metric.change !== undefined && (
              <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${
                metric.change >= 0 ? 'bg-crypto-gain/20 text-crypto-gain' : 'bg-crypto-loss/20 text-crypto-loss'
              }`}>
                {metric.change >= 0 ? '+' : ''}{metric.change.toFixed(2)}%
              </span>
            )}
          </div>
          <div>
            {metric.isLoading ? (
              <Skeleton className="w-24 h-8 mb-2" />
            ) : metric.isError ? (
              <p className="text-2xl font-bold font-mono text-crypto-text-muted">--</p>
            ) : (
              <p className="text-2xl font-bold font-mono">{metric.value}</p>
            )}
            <p className="text-xs text-crypto-text-muted mt-1">{metric.title}</p>
          </div>
          
          {/* Decorative element */}
          <div className="absolute -right-4 -bottom-4 w-16 h-16 rounded-full bg-current opacity-5" />
        </div>
      ))}
    </div>
  )
}
