import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api, { endpoints } from '@/config/api'
import { Skeleton } from '@/components/ui/Skeleton'

interface Transaction {
  id: string
  type: 'buy' | 'sell' | 'transfer_in' | 'transfer_out'
  symbol: string
  amount: number
  price: number
  total: number
  timestamp: string
  status: 'completed' | 'pending' | 'failed'
}

export default function Transactions() {
  const [filter, setFilter] = useState<string>('all')

  const { data: transactions, isLoading, isError } = useQuery({
    queryKey: ['transactions', filter],
    queryFn: async () => {
      const response = await api.get(endpoints.metrics.transactions, {
        params: { type: filter !== 'all' ? filter : undefined }
      })
      return response.data.transactions as Transaction[]
    },
    refetchInterval: 300000, // Poll every 5 minutes
  })

  const getTypeColor = (type: Transaction['type']) => {
    switch (type) {
      case 'buy': return 'text-crypto-gain'
      case 'sell': return 'text-crypto-loss'
      case 'transfer_in': return 'text-crypto-accent'
      case 'transfer_out': return 'text-yellow-400'
      default: return 'text-crypto-text'
    }
  }

  const getTypeLabel = (type: Transaction['type']) => {
    switch (type) {
      case 'buy': return 'Buy'
      case 'sell': return 'Sell'
      case 'transfer_in': return 'Transfer In'
      case 'transfer_out': return 'Transfer Out'
      default: return type
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-crypto-text">Transactions</h1>
        <div className="flex items-center gap-2">
          {['all', 'buy', 'sell', 'transfer_in', 'transfer_out'].map((type) => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                filter === type
                  ? 'bg-crypto-accent text-crypto-bg'
                  : 'bg-crypto-bg-secondary text-crypto-text-secondary hover:text-crypto-text'
              }`}
            >
              {type === 'all' ? 'All' : getTypeLabel(type as Transaction['type'])}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-crypto-bg-secondary rounded-xl border border-crypto-border overflow-hidden">
        {isLoading ? (
          <div className="divide-y divide-crypto-border">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="px-6 py-4 flex items-center justify-between">
                <div className="flex gap-4 items-center">
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-4 w-12" />
                </div>
                <div className="flex gap-8 items-center">
                  <Skeleton className="h-4 w-16" />
                  <Skeleton className="h-4 w-16" />
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-6 w-20 rounded" />
                </div>
              </div>
            ))}
          </div>
        ) : isError ? (
          <div className="p-12 text-center">
            <p className="text-crypto-loss mb-4">Failed to load transactions</p>
            <button 
              onClick={() => window.location.reload()}
              className="btn btn-primary"
            >
              Try Again
            </button>
          </div>
        ) : !transactions?.length ? (
          <div className="p-8 text-center text-crypto-text-muted">
            No transactions found
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-crypto-bg-tertiary">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-crypto-text-muted uppercase">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-crypto-text-muted uppercase">Asset</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-crypto-text-muted uppercase">Amount</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-crypto-text-muted uppercase">Price</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-crypto-text-muted uppercase">Total</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-crypto-text-muted uppercase">Date</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-crypto-text-muted uppercase">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-crypto-border">
              {transactions.map((tx) => (
                <tr key={tx.id} className="hover:bg-crypto-bg-tertiary/50 transition-colors">
                  <td className="px-6 py-4">
                    <span className={`font-medium ${getTypeColor(tx.type)}`}>
                      {getTypeLabel(tx.type)}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-crypto-text font-medium">{tx.symbol}</td>
                  <td className="px-6 py-4 text-right text-crypto-text">{tx.amount.toFixed(6)}</td>
                  <td className="px-6 py-4 text-right text-crypto-text">${tx.price.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right text-crypto-text font-medium">${tx.total.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right text-crypto-text-secondary">
                    {new Date(tx.timestamp).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      tx.status === 'completed' ? 'bg-crypto-gain/20 text-crypto-gain' :
                      tx.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-crypto-loss/20 text-crypto-loss'
                    }`}>
                      {tx.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
