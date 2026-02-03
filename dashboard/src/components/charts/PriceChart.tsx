import { useMemo } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from 'recharts'
import { usePriceHistory } from '../../hooks/usePrices'
import { PriceHistory } from '../../types'

interface PriceChartProps {
  symbol: string
  timeframe?: PriceHistory['timeframe']
  showVolume?: boolean
  height?: number
}

export default function PriceChart({
  symbol,
  timeframe = '24h',
  showVolume = false,
  height = 300,
}: PriceChartProps) {
  const { data: priceHistory, isLoading, error } = usePriceHistory(symbol, timeframe)

  const chartData = useMemo(() => {
    if (!priceHistory?.prices) return []
    return priceHistory.prices.map((p) => ({
      time: new Date(p.timestamp).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
      }),
      price: p.price,
      volume: p.volume,
    }))
  }, [priceHistory])

  const priceChange = useMemo(() => {
    if (chartData.length < 2) return 0
    const first = chartData[0].price
    const last = chartData[chartData.length - 1].price
    return ((last - first) / first) * 100
  }, [chartData])

  const isPositive = priceChange >= 0
  const strokeColor = isPositive ? '#00ff88' : '#ff4757'
  const gradientId = `gradient-${symbol}`

  if (isLoading) {
    return (
      <div className="card" style={{ height }}>
        <div className="h-full flex items-center justify-center">
          <div className="animate-pulse text-crypto-text-muted">Loading chart...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card" style={{ height }}>
        <div className="h-full flex items-center justify-center">
          <div className="text-crypto-loss">Failed to load chart data</div>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold">{symbol} Price</h3>
          <p className="text-sm text-crypto-text-secondary">Last {timeframe}</p>
        </div>
        <div className={`text-lg font-bold ${isPositive ? 'price-up' : 'price-down'}`}>
          {isPositive ? '+' : ''}{priceChange.toFixed(2)}%
        </div>
      </div>

      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={chartData} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={strokeColor} stopOpacity={0.3} />
              <stop offset="100%" stopColor={strokeColor} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
          <XAxis
            dataKey="time"
            stroke="#6b6b7b"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <YAxis
            stroke="#6b6b7b"
            fontSize={12}
            tickLine={false}
            axisLine={false}
            tickFormatter={(value) => `$${value.toLocaleString()}`}
            domain={['auto', 'auto']}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1a1a2e',
              border: '1px solid #2a2a4a',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#a0a0b0' }}
            formatter={(value: number) => [`$${value.toLocaleString()}`, 'Price']}
          />
          <Area
            type="monotone"
            dataKey="price"
            stroke={strokeColor}
            strokeWidth={2}
            fill={`url(#${gradientId})`}
          />
        </AreaChart>
      </ResponsiveContainer>

      {showVolume && chartData.length > 0 && (
        <div className="mt-4 pt-4 border-t border-crypto-border">
          <ResponsiveContainer width="100%" height={80}>
            <LineChart data={chartData}>
              <Line
                type="monotone"
                dataKey="volume"
                stroke="#00d9ff"
                strokeWidth={1}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
