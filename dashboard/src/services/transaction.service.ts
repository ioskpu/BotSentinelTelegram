import api, { endpoints } from '../config/api'

export interface Transaction {
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

export interface TransactionResponse {
  transactions: Transaction[]
  daily_stats: any[]
  total_count: number
  total_volume: number
}

export const transactionService = {
  async getTransactions(limit: number = 20, days: number = 30): Promise<TransactionResponse> {
    const response = await api.get(endpoints.metrics.transactions, {
      params: { limit, days }
    })
    return response.data
  },

  async getRecentTransactions(limit: number = 5): Promise<Transaction[]> {
    const response = await api.get(endpoints.metrics.transactions, {
      params: { limit }
    })
    return response.data.transactions
  }
}
