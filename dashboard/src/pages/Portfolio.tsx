import { useQuery } from '@tanstack/react-query'
import api, { endpoints } from '../config/api'
import { PortfolioSummary } from '../types'
import PriceChart from '../components/charts/PriceChart'

export default function Portfolio() {
  const { data: portfolio, isLoading, isError } = useQuery({
    queryKey: ['portfolio'],
    queryFn: async () => {
      const response = await api.get<PortfolioSummary>(endpoints.portfolio.get)
      return response.data
    },
    refetchInterval: 300000, // Sync every 5 minutes
  })

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-8 bg-crypto-bg-tertiary rounded w-48 mb-2" />
          <div className="h-4 bg-crypto-bg-tertiary rounded w-64" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-20 bg-crypto-bg-tertiary rounded" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <p className="text-crypto-loss mb-4">Failed to load portfolio data</p>
        <button 
          onClick={() => window.location.reload()}
          className="btn btn-primary"
        >
          Try Again
        </button>
      </div>
    )
  }

  const isPositive = (portfolio?.total_profit_loss_percent ?? 0) >= 0

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Portfolio</h1>
          <p className="text-crypto-text-secondary">
            Track your crypto holdings and performance
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <p className="stat-label">Total Value</p>
          <p className="stat-value text-2xl">
            ${(portfolio?.total_value ?? 0).toLocaleString()}
          </p>
        </div>

        <div className="card">
          <p className="stat-label">Total P&L</p>
          <p className={`stat-value ${isPositive ? 'text-crypto-gain' : 'text-crypto-loss'}`}>
            {isPositive ? '+' : ''}${(portfolio?.total_profit_loss ?? 0).toLocaleString()}
          </p>
        </div>

        <div className="card">
          <p className="stat-label">P&L %</p>
          <p className={`stat-value ${isPositive ? 'text-crypto-gain' : 'text-crypto-loss'}`}>
            {isPositive ? '+' : ''}{(portfolio?.total_profit_loss_percent ?? 0).toFixed(2)}%
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Holdings</h3>
          {!portfolio?.holdings || portfolio.holdings.length === 0 ? (
            <div className="text-center py-12 text-crypto-text-muted">
              <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
              <p>No holdings yet</p>
              <p className="text-sm mt-2">Add your first holding to start tracking</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-crypto-border">
                    <th className="table-header table-cell">Asset</th>
                    <th className="table-header table-cell text-right">Amount</th>
                    <th className="table-header table-cell text-right">Value</th>
                    <th className="table-header table-cell text-right">P&L</th>
                    <th className="table-header table-cell text-right">Allocation</th>
                  </tr>
                </thead>
                <tbody>
                  {portfolio.holdings.map((holding) => {
                    const holdingPositive = holding.profitLossPercent >= 0
                    return (
                      <tr key={holding.symbol} className="border-b border-crypto-border hover:bg-crypto-bg-tertiary transition-colors">
                        <td className="table-cell">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-full bg-crypto-bg-tertiary flex items-center justify-center font-mono font-bold text-crypto-accent text-sm">
                              {holding.symbol.slice(0, 2)}
                            </div>
                            <div>
                              <p className="font-medium">{holding.symbol}</p>
                              <p className="text-xs text-crypto-text-muted">{holding.name}</p>
                            </div>
                          </div>
                        </td>
                        <td className="table-cell text-right font-mono">
                          {holding.amount.toLocaleString()}
                        </td>
                        <td className="table-cell text-right font-mono">
                          ${holding.value.toLocaleString()}
                        </td>
                        <td className={`table-cell text-right font-mono ${holdingPositive ? 'text-crypto-gain' : 'text-crypto-loss'}`}>
                          {holdingPositive ? '+' : ''}{holding.profitLossPercent.toFixed(2)}%
                        </td>
                        <td className="table-cell text-right">
                          <div className="flex items-center justify-end gap-2">
                            <div className="w-16 h-2 bg-crypto-bg-tertiary rounded-full overflow-hidden">
                              <div
                                className="h-full bg-crypto-accent rounded-full"
                                style={{ width: `${holding.allocation}%` }}
                              />
                            </div>
                            <span className="text-sm text-crypto-text-secondary w-12 text-right">
                              {holding.allocation.toFixed(1)}%
                            </span>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <PriceChart symbol="BTC" timeframe="7d" height={250} />
          <PriceChart symbol="ETH" timeframe="7d" height={250} />
        </div>
      </div>
    </div>
  )
}
