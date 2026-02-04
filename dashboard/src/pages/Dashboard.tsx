import { MetricsCards, AlertsPanel, RecentTransactions, LiveFeed } from '@/components/dashboard'
import PriceChart from '@/components/charts/PriceChart'
import { usePrices } from '@/hooks/usePrices'

export default function Dashboard() {
  const { prices } = usePrices(['bitcoin', 'ethereum', 'solana', 'avalanche-2', 'stellar'])

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gradient">Dashboard</h1>
          <p className="text-crypto-text-secondary">
            Welcome back! Here's your crypto overview.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-crypto-text-muted">Last updated:</span>
          <span className="text-xs text-crypto-text-secondary">
            {new Date().toLocaleTimeString()}
          </span>
        </div>
      </div>

      {/* Metrics Cards */}
      <MetricsCards />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Price Chart - 2 columns */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Bitcoin Price</h3>
              <div className="flex items-center gap-2">
                {['1H', '24H', '7D', '30D'].map((tf) => (
                  <button
                    key={tf}
                    className="px-3 py-1 text-xs font-medium rounded-lg bg-crypto-bg-tertiary text-crypto-text-secondary hover:text-crypto-text hover:bg-crypto-accent/20 transition-colors"
                  >
                    {tf}
                  </button>
                ))}
              </div>
            </div>
            <PriceChart symbol="BTC" timeframe="24h" height={350} />
          </div>
        </div>

        {/* Live Feed - 1 column */}
        <div className="lg:col-span-1 h-[450px]">
          <LiveFeed />
        </div>
      </div>

      {/* Alerts and Transactions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AlertsPanel />
        <RecentTransactions />
      </div>

      {/* Top Performers */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Market Overview</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          {prices
            .sort((a, b) => (b.price_change_percentage_24h || 0) - (a.price_change_percentage_24h || 0))
            .map((price) => (
              <div
                key={price.symbol}
                className="p-4 rounded-xl bg-crypto-bg-tertiary/50 hover:bg-crypto-bg-tertiary transition-all duration-300 hover:scale-[1.02] cursor-pointer group"
              >
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-crypto-accent/20 to-crypto-purple/20 flex items-center justify-center font-mono font-bold text-sm text-crypto-accent group-hover:from-crypto-accent/30 group-hover:to-crypto-purple/30 transition-colors">
                    {price.symbol.slice(0, 2)}
                  </div>
                  <div>
                    <p className="font-semibold">{price.symbol}</p>
                    <p className="text-xs text-crypto-text-muted">{price.name}</p>
                  </div>
                </div>
                <div className="flex items-end justify-between">
                  <p className="font-mono font-bold text-lg">
                    ${(price.current_price || 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}
                  </p>
                  <p className={`text-sm font-medium ${
                    (price.price_change_percentage_24h || 0) >= 0 ? 'text-crypto-gain' : 'text-crypto-loss'
                  }`}>
                    {(price.price_change_percentage_24h || 0) >= 0 ? '+' : ''}{(price.price_change_percentage_24h || 0).toFixed(2)}%
                  </p>
                </div>
                {/* Mini sparkline placeholder */}
                <div className="mt-2 h-8 flex items-end gap-0.5">
                  {(price.sparkline || Array(12).fill(0).map(() => Math.random())).slice(-12).map((v, i) => (
                    <div
                      key={i}
                      className={`flex-1 rounded-t ${
                        (price.price_change_percentage_24h || 0) >= 0 ? 'bg-crypto-gain/40' : 'bg-crypto-loss/40'
                      }`}
                      style={{ height: `${(v as number) * 100}%` }}
                    />
                  ))}
                </div>
              </div>
            ))}
        </div>
      </div>
    </div>
  )
}
