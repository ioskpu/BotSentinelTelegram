import { useMemo } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import { Alert } from '../../types'

interface AlertsChartProps {
  alerts: Alert[]
  type?: 'bar' | 'pie'
  height?: number
}

const COLORS = ['#00d9ff', '#00ff88', '#ff4757', '#ffa502', '#a55eea']

export default function AlertsChart({ alerts, type = 'bar', height = 250 }: AlertsChartProps) {
  const alertsByType = useMemo(() => {
    const grouped = alerts.reduce((acc, alert) => {
      acc[alert.type] = (acc[alert.type] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return Object.entries(grouped).map(([name, value]) => ({
      name: name.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
      value,
    }))
  }, [alerts])

  const alertsBySymbol = useMemo(() => {
    const grouped = alerts.reduce((acc, alert) => {
      acc[alert.symbol] = (acc[alert.symbol] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return Object.entries(grouped)
      .map(([symbol, count]) => ({ symbol, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10)
  }, [alerts])

  if (alerts.length === 0) {
    return (
      <div className="card" style={{ height }}>
        <div className="h-full flex items-center justify-center">
          <div className="text-crypto-text-muted">No alerts to display</div>
        </div>
      </div>
    )
  }

  if (type === 'pie') {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Alerts by Type</h3>
        <ResponsiveContainer width="100%" height={height}>
          <PieChart>
            <Pie
              data={alertsByType}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={5}
              dataKey="value"
            >
              {alertsByType.map((_, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#1a1a2e',
                border: '1px solid #2a2a4a',
                borderRadius: '8px',
              }}
            />
          </PieChart>
        </ResponsiveContainer>
        <div className="flex flex-wrap justify-center gap-4 mt-4">
          {alertsByType.map((entry, index) => (
            <div key={entry.name} className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              <span className="text-sm text-crypto-text-secondary">
                {entry.name} ({entry.value})
              </span>
            </div>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Alerts by Symbol</h3>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={alertsBySymbol} margin={{ top: 5, right: 5, left: 5, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a2a4a" />
          <XAxis
            dataKey="symbol"
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
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#1a1a2e',
              border: '1px solid #2a2a4a',
              borderRadius: '8px',
            }}
            labelStyle={{ color: '#a0a0b0' }}
          />
          <Bar dataKey="count" fill="#00d9ff" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
