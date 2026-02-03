import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import api from '@/config/api'

interface Transaction {
  id: string
  type: 'buy' | 'sell' | 'transfer_in' | 'transfer_out'
  symbol: string
  amount: number
  price: number
  total: number
  timestamp: string
  status: 'completed' | 'pending' | 'failed'
  hash?: string
}

export default function RecentTransactions() {
  const { data: transactions, isLoading } = useQuery({
    queryKey: ['recentTransactions'],
    queryFn: async () => {
      const response = await api.get('/v1/metrics/transactions', {
        params: { limit: 5 }
      })
      return response.data.transactions as Transaction[]
    },
  })

  const getTypeConfig = (type: Transaction['type']) => {
    switch (type) {
      case 'buy':
        return { icon: '↓', color: 'text-crypto-gain', bg: 'bg-crypto-gain/10', label: 'Buy' }
      case 'sell':
        return { icon: '↑', color: 'text-crypto-loss', bg: 'bg-crypto-loss/10', label: 'Sell' }
      case 'transfer_in':
        return { icon: '→', color: 'text-crypto-accent', bg: 'bg-crypto-accent/10', label: 'In' }
      case 'transfer_out':
        return { icon: '←', color: 'text-crypto-purple', bg: 'bg-crypto-purple/10', label: 'Out' }
      default:
        return { icon: '•', color: 'text-crypto-text', bg: 'bg-crypto-bg-tertiary', label: type }
    }
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    
    if (hours < 1) return 'Just now'
    if (hours < 24) return `${hours}h ago`
    if (hours < 48) return 'Yesterday'
    return date.toLocaleDateString()
  }

  const demoTransactions: Transaction[] = [
    { id: '1', type: 'buy', symbol: 'BTC', amount: 0.05, price: 67500, total: 3375, timestamp: new Date().toISOString(), status: 'completed' },
    { id: '2', type: 'sell', symbol: 'ETH', amount: 2.5, price: 3450, total: 8625, timestamp: new Date(Date.now() - 3600000).toISOString(), status: 'completed' },
    { id: '3', type: 'transfer_in', symbol: 'SOL', amount: 100, price: 150, total: 15000, timestamp: new Date(Date.now() - 7200000).toISOString(), status: 'completed' },
    { id: '4', type: 'buy', symbol: 'AVAX', amount: 50, price: 35, total: 1750, timestamp: new Date(Date.now() - 86400000).toISOString(), status: 'pending' },
  ]

  const displayTransactions = transactions?.length ? transactions : demoTransactions

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Recent Transactions</h3>
        <Link
          to="/transactions"
          className="text-crypto-accent hover:text-crypto-accent-hover text-sm font-medium"
        >
          View All →
        </Link>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <div className="w-8 h-8 border-2 border-crypto-accent border-t-transparent rounded-full animate-spin" />
        </div>
      ) : displayTransactions.length === 0 ? (
        <div className="text-center py-8 text-crypto-text-muted">
          <p>No transactions yet</p>
        </div>
      ) : (
        <div className="space-y-3">
          {displayTransactions.map((tx) => {
            const config = getTypeConfig(tx.type)
            return (
              <div
                key={tx.id}
                className="flex items-center justify-between p-3 rounded-lg bg-crypto-bg-tertiary/30 hover:bg-crypto-bg-tertiary/50 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-full ${config.bg} flex items-center justify-center`}>
                    <span className={`text-lg font-bold ${config.color}`}>{config.icon}</span>
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{config.label}</span>
                      <span className="font-mono text-crypto-accent">{tx.symbol}</span>
                    </div>
                    <p className="text-sm text-crypto-text-muted">
                      {tx.amount} @ ${tx.price.toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`font-mono font-semibold ${
                    tx.type === 'buy' || tx.type === 'transfer_in' ? 'text-crypto-gain' : 'text-crypto-loss'
                  }`}>
                    {tx.type === 'buy' || tx.type === 'transfer_in' ? '+' : '-'}${tx.total.toLocaleString()}
                  </p>
                  <div className="flex items-center gap-2 justify-end">
                    <span className={`text-xs ${
                      tx.status === 'completed' ? 'text-crypto-gain' :
                      tx.status === 'pending' ? 'text-crypto-warning' :
                      'text-crypto-loss'
                    }`}>
                      {tx.status}
                    </span>
                    <span className="text-xs text-crypto-text-muted">{formatDate(tx.timestamp)}</span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
