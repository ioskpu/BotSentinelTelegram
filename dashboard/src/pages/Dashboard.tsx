import { useQuery } from '@tanstack/react-query'
import api, { endpoints } from '../config/api'
import { DashboardStats, ApiResponse } from '../types'
import StatsCard from '../components/dashboard/StatsCard'
import RecentActivity from '../components/dashboard/RecentActivity'
import PriceChart from '../components/charts/PriceChart'
import AlertsChart from '../components/charts/AlertsChart'
import { useAlerts } from '../hooks/useAlerts'
import { usePrices } from '../hooks/usePrices'

export default function Dashboard() {
  const { data: stats, isLoading: isLoadingStats } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: async () => {
      const response = await api.get<ApiResponse<DashboardStats>>(endpoints.dashboard.stats)
      return response.data.data
    },
  })

  const { alerts } = useAlerts({ pageSize: 100 })
  const { prices } = usePrices(['BTC', 'ETH', 'SOL', 'BNB'])

  const btcPrice = prices.find((p) => p.symbol === 'BTC')

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-crypto-text-secondary">
            Welcome back! Here's your crypto overview.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Portfolio Value"
          value={isLoadingStats ? '...' : `$${(stats?.portfolioValue || 0).toLocaleString()}`}
          change={stats?.portfolioChangePercent24h}
          changeLabel="24h"
          trend={stats?.portfolioChangePercent24h && stats.portfolioChangePercent24h >= 0 ? 'up' : 'down'}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />

        <StatsCard
          title="Active Alerts"
          value={isLoadingStats ? '...' : stats?.activeAlerts || 0}
          trend="neutral"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
          }
        />

        <StatsCard
          title="Triggered Today"
          value={isLoadingStats ? '...' : stats?.triggeredToday || 0}
          trend="up"
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          }
        />

        <StatsCard
          title="BTC Price"
          value={btcPrice ? `$${btcPrice.price.toLocaleString()}` : '...'}
          change={btcPrice?.changePercent24h}
          changeLabel="24h"
          trend={btcPrice?.changePercent24h && btcPrice.changePercent24h >= 0 ? 'up' : 'down'}
          icon={
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          }
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <PriceChart symbol="BTC" timeframe="24h" height={350} />
        </div>
        <div>
          <AlertsChart alerts={alerts} type="pie" height={200} />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Top Performers</h3>
          <div className="space-y-4">
            {prices
              .sort((a, b) => b.changePercent24h - a.changePercent24h)
              .slice(0, 5)
              .map((price) => (
                <div key={price.symbol} className="flex items-center justify-between p-3 rounded-lg hover:bg-crypto-bg-tertiary transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-crypto-bg-tertiary flex items-center justify-center font-mono font-bold text-crypto-accent">
                      {price.symbol.slice(0, 2)}
                    </div>
                    <div>
                      <p className="font-medium">{price.symbol}</p>
                      <p className="text-sm text-crypto-text-secondary">{price.name}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-mono font-semibold">${price.price.toLocaleString()}</p>
                    <p className={price.changePercent24h >= 0 ? 'price-up' : 'price-down'}>
                      {price.changePercent24h >= 0 ? '+' : ''}{price.changePercent24h.toFixed(2)}%
                    </p>
                  </div>
                </div>
              ))}
          </div>
        </div>

        <RecentActivity />
      </div>
    </div>
  )
}
